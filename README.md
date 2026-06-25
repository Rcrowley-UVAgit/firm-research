# Firm Research

A Claude Code plugin that brings primary-source research and diligence in house,
as an orchestrated multi-agent pipeline. A conductor runs specialized subagents
in sequence over free public data: scope the target, capture the record, rebuild
the real numbers, resolve who is behind what, verify every load-bearing claim,
red-team the finding, and write it up. Every workflow is direction-neutral; it
reports what the record shows.

The plugin is general-purpose by construction. Nothing is hardcoded to any
company. Point it at whatever you are looking at: a ticker, a URL, a person, an
entity. Run the whole pipeline with `diligence-pipeline`, or call any single
skill on its own.

## Install

```
/plugin marketplace add Rcrowley-UVAgit/firm-research
/plugin install firm-research@firm-research-marketplace
```

Or add the directory as a local marketplace and enable it from `/plugin`.

## What is in it

### The pipeline (orchestration)

- **diligence-pipeline**: the conductor. Runs the stage agents in sequence
  (scout, capture, reconstruct, resolve, claim-check, red-team-review, report),
  carries a structured handoff between stages, fans claim-check out one subagent
  per claim, and stops early if the target has no primary surface or red-team
  returns hold. Run it for a full work-up; the skills below are also callable on
  their own.

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

### Agents (the pipeline stages)

- **scout**: scope a target into a research plan: the checkable questions, the
  entities and tickers in scope, and which primary source answers each.
- **capture**: pull the primary record and what changed: filing diffs, recovered
  page source, background traffic, Wayback history.
- **reconstruct**: rebuild the independent numbers from public data (demand,
  trade, federal awards) and set them against the reported figures.
- **resolve**: map the entities and people behind a company across registries;
  resolve nominally independent parties by shared officer or address.
- **claim-check**: test one specific claim against the primary record; returns
  confirmed, broken, or unresolved, with citations.
- **red-team-review**: adversarially stress-test a finding before it ships: is
  it new, is it right, is it sourced, where is it weakest.
- **report**: synthesize the confirmed, checked findings into the Firm's house
  format, with a Source line on every exhibit.

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

The plugin is a pipeline of agents, not a pile of tools. `diligence-pipeline`
is the conductor: it runs the stage agents in sequence and carries a structured
handoff between them, so each agent works in its own context and passes forward
only what the next stage needs. scout plans, capture pulls the record,
reconstruct rebuilds the real number, and resolve maps who is behind what; these
three middle stages are independent once scout has routed the questions, so the
conductor runs them concurrently. claim-check then fans out, one subagent per
load-bearing claim, and red-team-review attacks the assembled finding before
report writes it up. The conductor stops early when a target has no primary
surface or when red-team returns hold. The skills are the tools the agents
wield, and any one is still callable on its own. Source attribution is mandatory
throughout: a number that loses its source is dropped at the handoff.
