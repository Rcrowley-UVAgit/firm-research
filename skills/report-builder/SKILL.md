---
name: report-builder
description: Assemble verified findings into a clean, fully sourced research write-up in the Firm's house format. Use when turning research notes or a set of findings into a structured draft, or when an existing draft needs to be organized and source-checked. Enforces the house conventions: a one-line thesis, a bulleted summary where each bullet is a self-contained sourced claim, an evidence-driven body where every exhibit carries a Source line, a quantified impact, and a disclaimer. Every claim must trace to a primary source.
argument-hint: "[topic-or-notes-path] [output-path]"
allowed-tools: Read, Write, Edit, Bash
---

# Report builder

Turn verified findings into a draft that an intelligent and adversarial reader will trust. The input is `$ARGUMENTS` (a topic, or a path to research notes, plus where to write the draft).

## Structure (the house format)

Use the template at `templates/report.md`. The sections, in order:

1. **Title and one-line thesis.** A specific, falsifiable statement of the finding.
2. **Summary of findings.** A bulleted list where each bullet is one self-contained claim that carries its own evidence. A reader who reads only this section should get the whole case.
3. **Background.** How the business or situation actually works, stated neutrally, so the evidence that follows lands.
4. **Evidence.** One section per sub-finding. Each is built bottom-up from primary documents. Every figure, screenshot, table, or quote carries a `Source:` line naming the exact system or document (for example `Source: SEC 10-K, FY2025, p.74` or `Source: UK Companies House`). Quote management's own words exactly, dated and attributed, then show the contradicting record.
5. **Quantified impact.** The numbers that follow from the evidence, framed conservatively and labeled as such.
6. **Conclusion.** What the evidence supports, stated without overreach.
7. **Disclaimer.** The standard language; keep it.

## Rules (non-negotiable)

- **Source everything.** Every exhibit and every load-bearing number gets a `Source:` line. A claim without a source does not go in.
- **Direction-neutral.** State what the record shows. Do not editorialize a trade direction.
- **No filler.** Before declaring a draft done, strip throat-clearing and hedging.
- **Footnote the document IDs.** Accession numbers, case numbers, charge IDs, filing dates. The footnotes are the verifiability layer.
- **Verify before drafting.** If a finding has not been adversarially checked, route it through `red-team-review` first.

## Finish

After writing, do a provenance pass (every exhibit has a Source line) and a claim-to-source pass (every number traces to a primary document). Report what you could not source.
