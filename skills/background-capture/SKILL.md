---
name: background-capture
description: Capture the data a webpage or app loads in the background but does not display, including the network requests it fires, the third-party domains it talks to, tracking and device identifiers, and analytics payloads. Use when a page is client-rendered, when you need the requests behind a site rather than its visible HTML, or when checking what data a property collects and where it sends it.
argument-hint: "[url] [optional: what to look for]"
allowed-tools: Read, Bash, WebFetch
---

# Background capture

The visible page is a fraction of what loads. This skill records the network activity behind a page: the requests it makes, the endpoints and third-party domains it contacts, and the payloads it sends and receives. The target is `$ARGUMENTS`.

## Method

1. **Drive a headless browser** (Playwright or Puppeteer via `npx`, or the Chrome automation tools if available) and load the URL.
2. **Record the network log.** Capture every request and response: URL, method, request headers and body, response status, and content type. Save the full HAR or an equivalent JSON log so the capture is reproducible.
3. **Classify the traffic.**
   - Third-party domains the page contacts (ad networks, analytics, trackers, data brokers), separated from first-party calls.
   - Identifiers in request payloads (device IDs, advertising IDs, cookies, fingerprinting signals).
   - Data that the page sends out versus data it pulls in.
   - API endpoints the page calls to build its content (these often return more than the page shows).
4. **Pull the hidden API responses.** When the page builds itself from a JSON API, fetch that endpoint directly; it frequently returns fields the page never renders.

## Output

A table of background requests grouped by first-party versus third-party, the identifiers observed, and any endpoint whose response carries more than the page displays. Save the network log file alongside the summary.

## Scope and caution

Only load and observe. Do not submit forms, log in, or transmit data on a target's behalf. Capturing traffic that a page itself initiates is observation; do not cross into interacting with private or authenticated surfaces.
