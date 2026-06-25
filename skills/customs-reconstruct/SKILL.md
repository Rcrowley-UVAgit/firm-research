---
name: customs-reconstruct
description: Reconstruct a company's physical trade activity from import and export records, independent of what the company reports. Use when a revenue line, a supplier relationship, a manufacturing claim, or a tariff position can be checked against shipment data; when imports may be shifting product category or port to change a duty or tax position; or when undisclosed counterparties appear as shippers or consignees. Rolls up shipments by counterparty, flags shifts in product category and port over time, and where shipment quantity is available, converts volume into an independent revenue estimate.
argument-hint: "[company-or-entity] [optional: claim to test]"
allowed-tools: Read, Bash, WebFetch, WebSearch
---

# Customs reconstruct

Customs records are an independent ledger of what physically moved. The target is `$ARGUMENTS`.

## Free source (default)

The US Census Bureau publishes aggregate trade statistics for free:
- **USA Trade Online** and the Census trade API (`https://api.census.gov/data/timeseries/intltrade/`) for imports and exports by HS commodity code, country, and port over time.
- Use these to detect category and port shifts and to size aggregate flows, even without shipment-level detail.

This gives the regime-shift signal (a sudden move from one HS code to another, or a concentration of entries at a new port of entry) without any paid feed.

## Optional premium slot (clearly labeled)

If `trade_data_api_key` and `trade_data_provider` are set in plugin config, use the named provider (ImportGenius, Panjiva, Tradesparq, Tradeindata) for **shipment-level bill-of-lading records**: named shipper, named consignee, dates, container counts, weights, and product descriptions. Without the key, say so and stay at the aggregate Census level.

## What to produce

1. **Counterparty rollup.** When shipment-level data is available, aggregate dollar or volume flows by shipper and consignee over the period. Surface counterparties that are not disclosed in the company's filings.
2. **Category-shift detection.** Track the HS codes the company imports over time. A move into a low-value or barely-used category timed to a tariff or duty event is a possible reclassification to change a duty position. Flag it with dates.
3. **Port-concentration shift.** Track port of entry over time; a sudden concentration at one port can accompany a category or routing change.
4. **Volume-to-revenue estimate.** When quantity is available (weight or units), convert it to a revenue estimate using a per-unit price derived from the company's own product listings (price and shipping weight), net of packaging. State the assumptions; this is an independent check on a reported revenue line.

## Output

The rollup or aggregate trend, any category or port shift with dates, and where used the volume-to-revenue estimate with its assumptions. Note clearly whether the analysis used free aggregate data or a shipment-level feed, and what a premium key would add.
