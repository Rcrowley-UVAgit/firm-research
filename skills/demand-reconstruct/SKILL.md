---
name: demand-reconstruct
description: Rebuild an independent read on real end-user demand or activity from free government data, as a substitute for a paid usage signal. Use when a company's reported revenue or growth should be checked against actual end-market usage; for a drug, the question of whether reported revenue reflects real dispensing or channel build; for a government-dependent business, whether reported revenue matches actual federal obligations; or for any business whose real activity is recorded in a public dataset. Matches the issuer's product or service to the public system that records its usage and compares that usage trend against what the company reports.
argument-hint: "[company-and-product] [optional: the claim to test]"
allowed-tools: Read, Bash, WebFetch, WebSearch
---

# Demand reconstruct

Many usage signals that vendors sell are reconstructable for free from the public system that records the activity. The job is to find the right system for the target's product, pull the usage history, and compare it to the reported number. The target is `$ARGUMENTS`.

## Match the product to its public record

- **Physician-administered drug** -> Medicare Part B. Find the drug's NDC from openFDA (`https://api.fda.gov/drug/ndc.json?search=brand_name:NAME`), map it to its HCPCS Level II J-code, then pull the code's Medicare claims, dosage units, and spending by year from the CMS data API. Compare utilization growth to reported product-revenue growth; a widening reported-to-dispensing gap is channel build. Helper: `python3 ${CLAUDE_SKILL_DIR}/scripts/ndc_lookup.py "BRAND"`.
  - CMS dataset list: `https://data.cms.gov/data.json` (find "Medicare Part B Spending by Drug").
  - Annual dataset: `https://data.cms.gov/data-api/v1/dataset/76a714ad-3a2c-43ac-b76d-9dadf8f7d890/data?size=6000` then filter rows by `HCPCS_Cd` or `Brnd_Name`.
  - Quarterly dataset uuid: `bf6a5b3b-31ee-4abb-b1ad-2607a1e7510a`.
  - Medicaid share: State Drug Utilization Data on data.medicaid.gov (per-year CSVs).
- **Drug with no script visibility (specialty pharmacy)** -> FDA adverse-event reports as a starts proxy. When a drug produces adverse events in most patients, the FAERS report curve tracks new starts. Pull FAERS (openFDA `https://api.fda.gov/drug/event.json?search=...`), bucket by earliest report date, and read the trend.
- **Government-dependent company** -> USAspending. POST to `https://api.usaspending.gov/api/v2/search/spending_by_award/` (and `spending_over_time`) with the recipient name to get actual federal obligations by year, a real-time read before the company reports. Check whether a touted contract is an IDIQ ceiling with little obligated, and whether revenue runs through acquired subsidiaries under different names.
- **Physical logistics or fleet claim** -> the DOT/FMCSA carrier registry for vehicles actually registered to the subsidiary, against the claimed delivery volume.
- **Data-center or energy site** -> the FCC broadband map for fiber providers at the site's county, and permit and tax-abatement filings for power and transmission, against the claimed capability.
- **Clinical or regulatory claim** -> ClinicalTrials.gov for trial status and history, and the FDA databases (see `fda-watch`).

## Method

1. Identify the product or service and the public system that records its real usage.
2. Pull the usage history from that system.
3. Pull the company's reported figure for the same periods from `edgar-forensics`.
4. Compare the two trends and quantify any gap. A reported line that grows faster than the underlying public usage is the finding; a usage trend that grows in lockstep kills the concern, which is just as valuable to know early.

## Discipline

Pull exact figures, not estimates. State the dataset, the identifier (NDC, J-code, recipient name), and the periods. If the public usage matches the reported number, say so plainly; an early kill is a real result.
