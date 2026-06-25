# Firm Research

A Claude Code plugin that brings primary-source research and diligence in house.
It turns recurring research bottlenecks into repeatable workflows: verify a
disclosure against the record, recover what a page no longer shows, reconstruct
real end-market activity from free public data, and map the entities and people
behind a company. Every workflow is direction-neutral; it reports what the
record shows.

The plugin is general-purpose by construction. Nothing is hardcoded to any
company. Point any skill at whatever you are looking at: a ticker, a URL, a
person, an entity.

## Install

```
/plugin marketplace add /path/to/firm-research
/plugin install firm-research@firm-research-marketplace
```

Or add the directory as a local marketplace and enable it from `/plugin`.

## What is in it

### Skills (run on free public data)

- **edgar-forensics**: pull a US issuer's filings from `data.sec.gov`; diff
  filings across periods to surface removed or changed disclosures; deep-read
  8-K exhibits for parties named only in attachments; extract related-party and
  concentration notes; build an insider and lock-up timeline from Form 4 and 144.
- **source-recover**: recover what a page carries in its raw source but does not
  display: scrubbed partner names, alt text, image filenames, meta tags,
  JSON-LD, hidden and commented-out blocks.
- **background-capture**: record the requests a page fires in the background,
  the third-party domains and identifiers it sends, and the API responses behind
  a client-rendered page.
- **wayback-diff**: diff a page against its Internet Archive history to find
  what quietly changed and when. Includes a working helper, `wayback_diff.py`.
- **registry-graph**: map entities and people across corporate registries;
  resolve "independent" entities to a common party by shared address or officer;
  flag any insider-controlled entity at the issuer's address; test whether a
  disclosed transaction is even feasible against the counterparty's capital and
  dissolution dates.
- **customs-reconstruct**: rebuild physical trade activity from import and
  export records; roll up by counterparty; flag category and port shifts; size a
  revenue line from shipment volume.
- **demand-reconstruct**: rebuild an independent read on real demand or activity
  from free government data (CMS Part B and NDC, FDA FAERS, USAspending, FCC,
  DOT, ClinicalTrials.gov) and compare it to the reported figure. Includes a
  working helper, `ndc_lookup.py`.
- **demand-provenance**: measure what share of a drug's real demand flows
  through the physicians its maker pays, by joining CMS Open Payments and
  Medicare Part D on physician NPI. Reports the paid-prescriber claim and cost
  share, prescriber concentration, and payment-nature mix. The complement to
  demand-reconstruct: that asks whether the demand is real, this asks whether it
  is bought. Includes a working helper, `provenance.py`.
- **report-builder**: assemble verified findings into the Firm's house format,
  with a Source line on every exhibit and a no-filler finish.

### Agents

- **claim-check**: test one specific claim against the primary record; returns
  confirmed, broken, or unresolved, with citations.
- **red-team-review**: adversarially stress-test a finding before it ships: is
  it new, is it right, is it sourced, where is it weakest.

### Hooks

- A draft check that warns on filler in written drafts.
- A session reminder of the evidentiary standard: source every load-bearing
  claim, pull exact figures, run red-team-review before a finding ships.

## Free out of the box, with labeled slots for premium feeds

Everything above runs on free public sources. Two techniques have an optional
premium tier, exposed as empty, clearly labeled config slots so the operator can
see exactly where a key drops in:

| Config slot | What it unlocks | Free fallback |
| --- | --- | --- |
| `opencorporates_api_key` | cross-jurisdiction officer and entity resolution at scale | SEC, US state Secretary of State portals, UK Companies House, ICIJ Offshore Leaks |
| `trade_data_api_key` + `trade_data_provider` | shipment-level bill-of-lading records (ImportGenius, Panjiva, Tradesparq, Tradeindata) | Census USA Trade Online aggregates |
| `firm_research_db_url` | reconcile findings against the Firm's own records | none |

Set `sec_user_agent` to a `Name email@domain` string; the SEC fair-access
policy requires it on every `data.sec.gov` request.

## Design notes

The skills are organized as one pipeline: capture what was said, capture what a
page or filing says now and said before, reconstruct the real number from an
independent public source, and resolve who is behind what. The agents add the
two cross-cutting moves: check a single claim, and stress-test a finding before
it is relied on. Source attribution is mandatory throughout.
