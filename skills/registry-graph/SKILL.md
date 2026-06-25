---
name: registry-graph
description: Map the entities and people behind a company across corporate registries and resolve who actually controls what. Use when checking for undisclosed related parties, when a counterparty or shareholder looks like a shell, when verifying that a disclosed transaction with a private entity is even feasible, or when an officer may control other entities that are not disclosed. Resolves entities by shared address, shared officer, and shared signatory; flags any officer-controlled entity that shares the issuer's headquarters; and tests disclosed transactions against the counterparty's registered capital and dissolution dates.
argument-hint: "[company-person-or-entity] [optional: relationship to test]"
allowed-tools: Read, Bash, WebFetch, WebSearch
---

# Registry graph

Public filings name entities; registries tell you who is behind them and whether they are real. The target is `$ARGUMENTS` (a company, a person, or an entity, with an optional relationship to test such as "is this disclosed vendor independent" or "did this acquisition payment actually happen").

## Free sources (default)

- **SEC EDGAR** for the issuer's officers, directors, related-party note, and HQ address.
- **US state Secretary of State** business registries (free in most states) to find entities by name, by officer, or by registered agent and address. Delaware, Florida, Wyoming, Texas, and the issuer's home state are common hiding spots.
- **UK Companies House** free API (`https://api.company-information.service.gov.uk/`) for officers, persons of significant control, and filing history.
- **ICIJ Offshore Leaks Database** (`https://offshoreleaks.icij.org/`) to connect entities and people to offshore structures named in the Panama, Paradise, and Pandora papers.
- **General web and news search** to seed names, addresses, and prior reporting.

## Optional premium slots (clearly labeled)

If the operator has set them in plugin config, use them; otherwise skip and rely on free sources, and say so in the output.

- `opencorporates_api_key`: OpenCorporates officer search returns every entity a named person is an officer of, across jurisdictions. This is the fastest path to undisclosed entities controlled by an insider. Without the key, approximate it with per-state SOS officer search.
- `firm_research_db_url`: reconcile findings against the Firm's own records.

## What to build

1. **Entity and officer graph.** From the issuer, enumerate officers, directors, and significant holders. For each, search the registries above for other entities they control or are registered to.
2. **Shared-attribute resolution.** Link "independent" entities to a common party by matching registered address, registered agent, officer, or signatory. A shared unit number or agent is the link.
3. **HQ-collision check.** Flag any officer-controlled entity that shares the issuer's headquarters address. An undisclosed entity operating from the issuer's own address, run by an insider, is the related-party finding.
4. **Feasibility test.** For any disclosed transaction with a private entity (an acquisition, a payment, a stake), pull that entity's registry record: registered capital, reported financials, and status and dates (active, dissolved, liquidated, struck off). Test the disclosed event against those dates and amounts. A payment dated after the counterparty was dissolved, or a "fund" backed by nominal capital, is the finding.
5. **Cross-check disclosure.** Compare the graph against the issuer's related-party note and concentration note. Anything in the graph but not in the note is undisclosed.

## Output

A short relationship map (entity, link type, source), the HQ-collision and feasibility findings stated plainly, and for each node the registry, jurisdiction, and document that supports it. Say which sources were free and where a premium key would have extended coverage.
