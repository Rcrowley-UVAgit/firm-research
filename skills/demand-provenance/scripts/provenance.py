#!/usr/bin/env python3
"""Measure what share of a drug's real demand flows through the physicians its
maker pays, by joining two free CMS datasets on physician NPI.

Usage:
    provenance.py --brand "Korlym" --mfr "corcept"
    provenance.py --brand "Korlym" --mfr "corcept" --json out.json --top 12
    provenance.py --brand "BRAND" --mfr "mfr substring" \
        --partd-uuid <uuid> --op-dist <distribution-id>

What it joins:
  - Part D Prescribers by Provider and Drug (who writes the scripts), by NPI,
    with claim count and drug cost.
  - Open Payments / Sunshine Act general payments (who the maker pays), by NPI,
    with payment amount and the nature of each transfer of value.

The intersection is the paid-prescriber claim share and cost share, the
prescriber concentration, and the payment-nature mix. A high paid share is
bought demand; a low share clears the name. That number is in no filing and
cannot be Googled.

--mfr is matched case-insensitively as a substring of the Open Payments
manufacturer name, so "corcept" catches "Corcept Therapeutics Incorporated".

Defaults: Part D 2023 dataset and Open Payments 2024 general-payment
distribution (both validated). Override with --partd-uuid / --op-dist to run an
earlier year; find prior-year ids in data.cms.gov/data.json and the Open
Payments datastore listing. Standard library only.
"""
import argparse
import collections
import json
import sys
import time
import urllib.parse
import urllib.request

UA = "Firm Research demand-provenance (research@firm.example)"

# Validated identifiers (see SKILL.md for the data layer and gotchas).
PARTD_UUID_2023 = "9552739e-3d05-4c1b-8eff-ecabf391e2e5"
OP_DIST_2024 = "9323b84e-cda3-5f6b-a501-b76926c7c035"

# Open Payments column names.
NPI = "covered_recipient_npi"
MFRC = "applicable_manufacturer_or_applicable_gpo_making_payment_name"
AMT = "total_amount_of_payment_usdollars"
NAT = "nature_of_payment_or_transfer_of_value"

# The NPI-in route is indexed and fast; a manufacturer-wide like-scan re-scans
# from offset 0 on every page and is slow past a few thousand rows. Pull the
# prescriber NPIs first, then ask Open Payments only about those NPIs in chunks.
NPI_CHUNK = 60
PAGE = 500  # DKAN datastore caps limit at 500.


def http(url, payload=None, timeout=120):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data:
        headers["Content-Type"] = "application/json"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def partd_prescribers(brand, uuid):
    """All Part D prescribers of a brand, keyed by NPI."""
    base = "https://data.cms.gov/data-api/v1/dataset/%s/data" % uuid
    presc = {}
    size, off = 5000, 0
    while True:
        q = urllib.parse.urlencode(
            {"filter[Brnd_Name]": brand, "size": str(size), "offset": str(off)}
        )
        rows = http(base + "?" + q)
        if not rows:
            break
        for r in rows:
            npi = r.get("Prscrbr_NPI")
            if not npi:
                continue
            presc[str(npi)] = {
                "clms": float(r.get("Tot_Clms") or 0),
                "cost": float(r.get("Tot_Drug_Cst") or 0),
                "name": ("%s %s" % (
                    r.get("Prscrbr_First_Name", ""),
                    r.get("Prscrbr_Last_Org_Name", ""))).strip(),
                "state": r.get("Prscrbr_State_Abrvtn"),
                "spec": r.get("Prscrbr_Type"),
            }
        off += len(rows)
        if len(rows) < size:
            break
    return presc


def payments_to(npis, mfr_substr, dist):
    """Open Payments general payments to a set of NPIs from one manufacturer.

    Uses the indexed NPI-in route in chunks and filters the manufacturer
    client-side, because a like-condition combined with an in-condition in the
    same DKAN query silently returns zero.
    """
    url = "https://openpaymentsdata.cms.gov/api/1/datastore/query/%s" % dist
    needle = mfr_substr.lower()
    paid = collections.defaultdict(
        lambda: {"amt": 0.0, "n": 0, "natures": collections.Counter()})
    mfr_name = None
    npis = list(npis)
    n_chunks = (len(npis) + NPI_CHUNK - 1) // NPI_CHUNK
    for ci in range(0, len(npis), NPI_CHUNK):
        chunk = npis[ci:ci + NPI_CHUNK]
        off = 0
        while True:
            r = http(url, {
                "conditions": [
                    {"property": NPI, "value": chunk, "operator": "in"}],
                "limit": PAGE, "offset": off,
            })
            res = r.get("results", [])
            for row in res:
                name = row.get(MFRC) or ""
                if needle not in name.lower():
                    continue
                npi = str(row.get(NPI) or "")
                if not npi or npi == "None":
                    continue
                mfr_name = mfr_name or name
                try:
                    amt = float(row.get(AMT) or 0)
                except (TypeError, ValueError):
                    amt = 0.0
                paid[npi]["amt"] += amt
                paid[npi]["n"] += 1
                paid[npi]["natures"][row.get(NAT)] += 1
            if len(res) < PAGE:
                break
            off += len(res)
        sys.stderr.write("  chunk %d/%d done\n" % (ci // NPI_CHUNK + 1, n_chunks))
        sys.stderr.flush()
    return paid, mfr_name


def main():
    ap = argparse.ArgumentParser(description="Bought-demand probe (paid-prescriber concentration).")
    ap.add_argument("--brand", required=True, help="Part D brand name, e.g. Korlym")
    ap.add_argument("--mfr", required=True, help="Open Payments manufacturer substring, e.g. corcept")
    ap.add_argument("--partd-uuid", default=PARTD_UUID_2023, help="Part D dataset uuid (default 2023)")
    ap.add_argument("--op-dist", default=OP_DIST_2024, help="Open Payments distribution id (default 2024)")
    ap.add_argument("--top", type=int, default=12, help="how many top paid prescribers to print")
    ap.add_argument("--json", help="optional path to write the headline numbers")
    a = ap.parse_args()

    presc = partd_prescribers(a.brand, a.partd_uuid)
    if not presc:
        sys.exit("No Part D prescribers found for brand %r. Check spelling or the dataset year." % a.brand)
    tc = sum(p["clms"] for p in presc.values())
    tk = sum(p["cost"] for p in presc.values())
    print("%s: %d Part D prescribers, %s claims, $%s drug cost"
          % (a.brand, len(presc), format(tc, ",.0f"), format(tk, ",.0f")), flush=True)

    paid, mfr_name = payments_to(presc.keys(), a.mfr, a.op_dist)
    both = set(presc) & set(paid)
    cp = sum(presc[n]["clms"] for n in both)
    kp = sum(presc[n]["cost"] for n in both)
    total_paid = sum(v["amt"] for v in paid.values())

    claim_share = 100 * cp / tc if tc else 0.0
    cost_share = 100 * kp / tk if tk else 0.0

    print("\n===== BOUGHT-DEMAND: %s / %s =====" % (a.brand, mfr_name or a.mfr))
    print("  prescribers also paid by the maker: %d/%d (%.0f%%)"
          % (len(both), len(presc), 100 * len(both) / len(presc)))
    print("  CLAIM share by paid prescribers: %.1f%%" % claim_share)
    print("  COST  share by paid prescribers: %.1f%% ($%s/$%s)"
          % (cost_share, format(kp, ",.0f"), format(tk, ",.0f")))

    top = sorted(presc.items(), key=lambda kv: kv[1]["clms"], reverse=True)[:10]
    top_share = 100 * sum(p["clms"] for _, p in top) / tc if tc else 0.0
    top_paid = sum(1 for n, _ in top if n in paid)
    print("  top-10 prescribers = %.1f%% of claims; paid %d/10" % (top_share, top_paid))
    print("  total maker $ to paid prescribers: $%s" % format(total_paid, ",.0f"))

    natures = collections.Counter()
    for n in both:
        for nat, k in paid[n]["natures"].items():
            natures[nat] += k
    if natures:
        print("  payment natures to paying-and-prescribing physicians:")
        for nat, k in natures.most_common(8):
            print("     %5d  %s" % (k, nat))

    if both:
        print("  top paid prescribers (by claims):")
        for n in sorted(both, key=lambda n: presc[n]["clms"], reverse=True)[:a.top]:
            print("     %-24s clms=%4.0f $%9s  %-24s %s"
                  % (presc[n]["name"][:24], presc[n]["clms"], format(paid[n]["amt"], ",.0f"),
                     (presc[n]["spec"] or "")[:24], presc[n]["state"]))

    if a.json:
        json.dump({
            "brand": a.brand, "manufacturer": mfr_name or a.mfr,
            "n_prescribers": len(presc), "total_claims": tc, "total_cost": tk,
            "n_paid_and_prescribing": len(both),
            "claim_share_pct": claim_share, "cost_share_pct": cost_share,
            "total_maker_payments": total_paid,
        }, open(a.json, "w"), indent=2)
        print("saved %s" % a.json)


if __name__ == "__main__":
    main()
