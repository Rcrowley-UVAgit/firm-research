---
name: edgar-forensics
description: Pull and forensically read a US issuer's SEC filings from primary sources. Use when the task involves a public company's 10-K, 10-Q, 8-K, proxy, or insider activity, or when a claim needs to be checked against the filing record. Diffs filings across periods to surface removed or changed disclosures, deep-reads 8-K exhibits for parties named only in attachments, extracts related-party notes, and builds an insider-transaction and lock-up timeline from Form 4 and 144 data.
argument-hint: "[ticker-or-CIK] [optional: claim or focus]"
allowed-tools: Read, Bash, WebFetch, WebSearch
---

# EDGAR forensics

Primary-source reading of a US issuer's filings. The target is `$ARGUMENTS` (a ticker, a CIK, or a company name plus an optional claim to test).

## Access pattern (read this first)

`data.sec.gov` and `www.sec.gov/Archives` reject WebFetch (403) and, in some sandboxes, return zero bytes to `curl`. Use Python `urllib.request` with a compliant User-Agent header. The User-Agent comes from the `sec_user_agent` plugin config (format `Name email@domain`).

- Submissions and filing list: `https://data.sec.gov/submissions/CIK##########.json` (CIK zero-padded to 10 digits).
- XBRL company concept (clean period values): `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/{Concept}.json` (e.g. `AccountsReceivableNetCurrent`, `RevenueFromContractWithCustomerExcludingAssessedTax`).
- Full-text search across filings (JSON): `https://efts.sec.gov/LATEST/search-index?q="exact phrase"&forms=10-K`. Returns matching filings with accession numbers. Use it to find which filing first or last contained a given phrase.
- Resolve ticker to CIK: `https://www.sec.gov/files/company_tickers.json`.

## What to produce

Run the analyses that fit the target and the claim. Each finding must cite the exact filing, date, and accession number.

1. **Disclosure diff across periods.** Compare the current 10-K (or 10-Q) against the prior one. Flag language that was *removed* (a deleted risk factor, a dropped supplier or customer concentration note, a director relationship that disappeared from a related-party section). Removals are often the signal; present the before text and the after text side by side.
2. **Exhibit deep-read.** Open the exhibits to recent 8-Ks, not just the press-release body. Names of counterparties, customers, and related parties are frequently disclosed only inside an exhibit agreement and never in the headline. List any party named in an exhibit but absent from the narrative disclosure.
3. **Related-party and concentration extraction.** Pull the related-party transactions note (Item 404 / the financial-statement note) and the customer or supplier concentration note. Record every named entity, the dollar amounts, and whether each is described as a customer or a vendor.
4. **Insider and lock-up timeline.** From the submissions feed, list Form 4 and Form 144 filings. Parse transaction codes from the Form 4 XML (S = open-market sale, P = purchase, F = tax withholding, M = option exercise, A = grant). Build a dated per-insider buy/sell timeline and an upcoming-unlock calendar from any lock-up or 10b5-1 adoptions disclosed.
5. **Quantitative read.** Pull the XBRL values needed to test the claim (receivables trend / DSO, operating cash versus reported earnings, segment or product disaggregation from the MD&A table). State the trend and what it implies.

## Discipline

Cite every number to a primary filing. Do not estimate when the exact value is available in XBRL or the filing text; pull it. Note explicitly anything you could not verify.
