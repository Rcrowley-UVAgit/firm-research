---
name: wayback-diff
description: Compare a webpage against its earlier captures to find what quietly changed and when. Use when checking whether a company altered a policy, a product or service description, a team or executive bio, a disclosure, or a marketing claim without announcing it. Pulls Internet Archive snapshots of a URL, diffs the text across dates, and pinpoints when wording was added, softened, or removed.
argument-hint: "[url] [optional: phrase or section to track]"
allowed-tools: Read, Bash, WebFetch
---

# Wayback diff

A quiet edit to a public page is a dated, sourced fact. This skill reconstructs the edit history of a URL from the Internet Archive. The target is `$ARGUMENTS` (a URL, optionally a phrase or section to track across time).

## Method

1. **List snapshots.** Query the Wayback CDX API for every capture of the URL:
   `http://web.archive.org/cdx/search/cdx?url=<URL>&output=json&fl=timestamp,original,statuscode,digest&collapse=digest`
   The `collapse=digest` parameter removes consecutive identical captures, so each row is a real change.
2. **Fetch the bracketing snapshots.** For the period in question, fetch the archived pages:
   `https://web.archive.org/web/<timestamp>id_/<URL>` (the `id_` suffix returns the raw archived bytes without the Archive's banner).
3. **Diff the text.** Strip tags and diff the visible text between dates. Report what was added, what was removed, and what was reworded.
4. **Date the change.** Bracket the change between the last snapshot that had the old wording and the first that had the new wording.
5. **Live versus archive.** Fetch the current live page and diff it against the most recent archived capture, so any change made after the last snapshot is also caught.

A helper that lists snapshots and diffs two of them is at `scripts/wayback_diff.py`:
`python3 ${CLAUDE_SKILL_DIR}/scripts/wayback_diff.py <URL>` to list, or add two timestamps to diff them.

## Output

The change, the two wordings in full, and the dates it sits between, with the snapshot URLs so it is independently verifiable. If a current page differs from its last archive, flag the live-versus-archive delta separately.
