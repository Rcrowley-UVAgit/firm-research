---
name: source-recover
description: Recover information that a webpage carries in its raw source but does not show on the rendered page. Use when checking whether a company or counterparty has scrubbed a partner name, logo, or claim from a site while leaving traces in the HTML, or when a page's visible text and its underlying source disagree. Compares raw source against rendered text and surfaces the difference (alt text, image filenames, meta tags, JSON-LD, structured data, and commented-out or hidden blocks).
argument-hint: "[url] [optional: term to look for]"
allowed-tools: Read, Bash, WebFetch
---

# Source recovery

A rendered page is an edited surface; the raw source often still carries what the surface removed. The target is `$ARGUMENTS` (a URL, optionally a term such as a former partner's name to look for).

## Method

1. **Fetch the raw HTML.** Use Python `urllib.request` (or `curl`) with a normal browser User-Agent. Save the raw bytes.
2. **Render the visible text.** Strip tags to get only what a reader would see on the page.
3. **Diff source against rendered.** Surface everything present in the source but absent from the visible text:
   - `alt` attributes and `<img>` `src` filenames (a removed partner logo often survives as `partner-logo-acme.png`).
   - `<meta>` tags, Open Graph and Twitter card fields, and `<title>` history.
   - JSON-LD and other structured-data blocks (`application/ld+json`), which frequently name parties, products, and prices the page no longer displays.
   - HTML comments and `display:none` / `hidden` / `aria-hidden` blocks.
   - Inline script config objects and data attributes.
4. **If given a term**, report every place the term appears in the source, and state whether it appears in the visible text. A term that is in the source but not on the page is the finding.
5. **Pair with history.** When a scrub is suspected, hand the URL to `wayback-diff` to date when the visible page changed while the source trace remained.

## Output

For each recovered item: the exact string, where it lives in the source (tag and attribute), whether it is visible on the page, and a one-line read on why it matters. Capture the raw source file so the finding is reproducible.

## Note on dynamic pages

For sites that build content with JavaScript, a static fetch may miss data loaded at runtime. When that happens, say so and route to `background-capture` (headless render plus network capture), which is the heavier tool for client-rendered pages.
