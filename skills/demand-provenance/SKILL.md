---
name: demand-provenance
description: Measure what share of a drug's real demand flows through the physicians its maker pays, by joining two free CMS datasets on physician NPI. Use when a company's drug revenue may rest on a narrow set of paid prescribers rather than organic adoption; when a short or long thesis turns on whether scripts come from doctors on the maker's payroll; when testing Anti-Kickback or False Claims exposure on a specialty drug; or to clear an organic name by showing its paid-prescriber share is low. This is the complement to demand-reconstruct: that skill asks whether the demand is real, this one asks whether the demand is bought. The linkage is in no filing and cannot be Googled.
argument-hint: "[brand drug and its maker] [optional: the claim to test]"
allowed-tools: Read, Bash, WebFetch, WebSearch
---

# Demand provenance

Two free federal datasets, joined on physician NPI, answer a question that
appears in no filing: what share of a drug's real demand comes from the
physicians its maker pays. A diligent reader Googling the company never finds
"84% of this drug's Medicare cost flows through doctors on the payroll." The
target is `$ARGUMENTS`.

## The join

- **Who the maker pays** -> CMS Open Payments (the Sunshine Act general-payment
  file), by physician NPI, with the payment amount and the nature of each
  transfer of value: food and beverage, travel, speaker fee, consulting,
  honoraria, royalty, ownership.
- **Who actually writes the scripts** -> CMS Medicare Part D Prescribers by
  Provider and Drug, by physician NPI, with claim count and drug cost.
- **The intersection** -> the paid-prescriber claim share and cost share, the
  prescriber concentration, and the payment-nature mix. Royalty or ownership to a
  high-volume prescriber is the strongest tell; speaker-and-meal saturation
  across the whole prescriber base is the structural one.

## Method

1. Resolve the brand to its Part D name and the maker to its Open Payments
   manufacturer name. If you start from a ticker, the issuer's 10-K names the
   drug; the manufacturer string is the legal entity (for example "Corcept
   Therapeutics Incorporated", matched on the substring "corcept").
2. Run the helper:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/provenance.py --brand "BRAND" --mfr "maker substring"`.
   It pulls every Part D prescriber of the brand, asks Open Payments which of
   those NPIs the maker paid, and reports the paid claim share, cost share,
   prescriber concentration, payment-nature mix, and the top paid prescribers.
   Add `--json out.json` to capture the headline numbers for `report-builder`.
3. Read the result against the reported story from `edgar-forensics`. A high
   paid-claim share next to a "broad and growing adoption" narrative is the
   finding. A low share kills the concern and clears the name, which is just as
   useful to know early.
4. For a physician-administered (specialty/biologic) drug with no Part D retail
   visibility, the scripts live in Medicare Part B by Provider and HCPCS, not
   Part D. Join the same way on NPI. Use `demand-reconstruct` to find the drug's
   J-code first, then point the same payment join at the Part B prescriber set.

## How to read the result

- **Paid-claim share** is the headline. The higher the share of claims and cost
  written by paid physicians, the more the revenue line depends on continued
  payments rather than organic medical demand.
- **Prescriber concentration** (the top-10 share, and how many of the top are
  paid) shows how few relationships the franchise rests on.
- **Payment nature** is the legal texture. Broad food-and-speaker saturation is
  the structural pattern; a royalty or ownership stake to a top prescriber is the
  individual red flag and the one most directly in Anti-Kickback territory.
- **The catalyst** is real: Anti-Kickback Statute and False Claims Act exposure,
  and the structural fragility of a revenue base that depends on the payments
  continuing. State it as exposure shown by the record, not as a legal
  conclusion.

## The data layer

- **Open Payments** general-payment file (DKAN datastore). 2024 distribution id
  `9323b84e-cda3-5f6b-a501-b76926c7c035`; prior years have their own ids in the
  datastore listing. Query:
  `POST https://openpaymentsdata.cms.gov/api/1/datastore/query/{distId}` with
  body `{"conditions":[...],"limit":<=500,"offset":N}`. Columns:
  `covered_recipient_npi`,
  `applicable_manufacturer_or_applicable_gpo_making_payment_name`,
  `total_amount_of_payment_usdollars`,
  `nature_of_payment_or_transfer_of_value`.
- **Part D Prescribers by Provider and Drug** (CMS data-api). 2023 dataset uuid
  `9552739e-3d05-4c1b-8eff-ecabf391e2e5`; prior years in
  `data.cms.gov/data.json`. Query:
  `GET https://data.cms.gov/data-api/v1/dataset/{uuid}/data?filter[Brnd_Name]=NAME&size=5000&offset=N`.
  Columns: `Prscrbr_NPI`, `Tot_Clms`, `Tot_Drug_Cst`, `Prscrbr_Type`,
  `Prscrbr_State_Abrvtn`, name fields.

### Gotchas baked into the helper

- DKAN `limit` maxes at 500; paginate with `offset` in the POST body.
- A `like` condition and an `in` condition in the same query silently return 0.
  Pull the prescriber NPIs first and ask Open Payments only about those NPIs with
  the indexed `in` operator, filtering the manufacturer name client-side.
- A manufacturer-wide `like %name%` scan re-scans from offset 0 on every page and
  gets slow past a few thousand rows. The NPI-`in` route is indexed and fast (six
  60-NPI chunks for Korlym, not a 34,550-row scan).
- Aggregate group-by queries return a database error; aggregate in Python.

## Worked example (the reference, run live)

Korlym (mifepristone, Cushing's syndrome), maker Corcept Therapeutics, 2023 Part
D against 2024 Open Payments: 318 Part D prescribers, 7,523 claims, $260.0M drug
cost. 249 of 318 prescribers (78%) are paid by Corcept. Paid prescribers wrote
85.3% of all claims and 84.1% of the cost ($218.8M of $260.0M). The top-10
prescribers are 13.7% of claims and all 10 are paid. Payment natures to the
paying-and-prescribing physicians run 2,828 food and beverage, 546 travel, 462
speaker, 61 honoraria, 36 consulting. Reproduce with
`provenance.py --brand "Korlym" --mfr "corcept"`.

## Discipline

Pull exact figures, not estimates. State the datasets, the program years, the
identifiers (brand, manufacturer string, NPI), and the claim and cost counts. If
the paid-prescriber share is low, say so plainly and clear the name; an honest
negative is a real result. Frame the payment pattern as what the record shows and
the legal exposure it implies, never as a finding of wrongdoing. Run the output
through `report-builder` so every figure carries its Source line, and through
`red-team-review` before it ships.
