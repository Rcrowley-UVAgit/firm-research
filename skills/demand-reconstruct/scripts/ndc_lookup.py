#!/usr/bin/env python3
"""Look up a drug's NDC and packaging from openFDA by brand name.

Usage:
    ndc_lookup.py "BRAND NAME"

Prints generic name, labeler, dosage form, route, and product NDCs. The
generic name and dosage form are what you carry to a HCPCS J-code crosswalk;
the J-code then drives the CMS Part B Spending by Drug pull. Standard library only.
"""
import sys
import json
import urllib.request
import urllib.parse

UA = "Firm Research demand-reconstruct (research@firm.example)"
BASE = "https://api.fda.gov/drug/ndc.json?search=brand_name:{q}&limit=20"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    brand = sys.argv[1]
    q = urllib.parse.quote(f'"{brand}"')
    try:
        data = fetch(BASE.format(q=q))
    except Exception as e:
        print(f"openFDA query failed: {e}")
        sys.exit(2)
    results = data.get("results", [])
    if not results:
        print(f"No NDC results for brand '{brand}'.")
        return
    seen = set()
    print(f"openFDA NDC matches for '{brand}':\n")
    for r in results:
        key = (r.get("generic_name"), r.get("labeler_name"), r.get("dosage_form"))
        if key in seen:
            continue
        seen.add(key)
        print(f"  product_ndc : {r.get('product_ndc')}")
        print(f"  brand       : {r.get('brand_name')}")
        print(f"  generic     : {r.get('generic_name')}")
        print(f"  labeler     : {r.get('labeler_name')}")
        print(f"  dosage form : {r.get('dosage_form')}")
        print(f"  route       : {', '.join(r.get('route', []) or [])}")
        print(f"  pharm class : {', '.join(r.get('pharm_class', []) or [])}")
        print()
    print("Next: map the generic + dosage form to its HCPCS J-code, then pull")
    print("the CMS Part B Spending by Drug dataset filtered on that HCPCS_Cd.")


if __name__ == "__main__":
    main()
