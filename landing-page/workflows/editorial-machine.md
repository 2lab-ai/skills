# Workflow: editorial-machine (default theme)

The default theme workflow for [`landing-page`](../SKILL.md). It builds a page in
the editorial composition grammar — warm-paper canvas, serif-led thesis, one
authored proof object, one rationed accent — in either lane.

**Dependency:** the sibling skill directory `editorial-machine/`, installed
alongside `landing-page/`. If it is absent, stop and say so; this workflow has
no embedded copy of the rules.

## Required reading

Read both in full before drafting. They are the contract; this file is only the
order of operations.

1. [`../../editorial-machine/references/source-analysis.md`](../../editorial-machine/references/source-analysis.md)
   — the evidence ledger (what was actually measured, and the anti-copy boundary).
2. [`../../editorial-machine/references/composition-system.md`](../../editorial-machine/references/composition-system.md)
   — the MUST/SHOULD/MAY rules: tokens §2, type §3, section grammar §4, proof
   objects §5, copy §6, responsive §7, motion §8, accessibility §9, performance
   §10 (§10.3 standalone lane, §10.4 existing-app lane), anti-copy §11,
   checklist §12.

Then follow [`../../editorial-machine/SKILL.md`](../../editorial-machine/SKILL.md),
which holds the full step-by-step workflow, the per-lane gates, and the output
contract.

## Order of operations

1. **Target contract + lane** — from [`../SKILL.md`](../SKILL.md) §1–§2. Carry the
   lane into every step below; it decides the implementation surface and the gates.
2. **Fact ledger** — every claim sourced, no invented metrics.
3. **Thesis + proof object** — one belief, one proof object unique to this product.
4. **Page brief** — thesis, proof object, section order and why, tokens with the
   *computed* contrast ratio, type roles, motion density, source line per claim.
5. **Implementation**
   - Lane A (existing app): author the route in the target repo's own stack and
     conventions. The grammar (tokens, section order, proof object, accessibility
     floor) is unchanged; the delivery mechanism is the app's.
   - Lane B (standalone): one self-contained `.html` file, no build step.
6. **Gates** — per lane, per `editorial-machine/SKILL.md` §Gates by lane. Lane B
   adds the deterministic validator; Lane A runs the app's own gates instead.
7. **Browser QA** — both lanes, at the real delivery URL from the target contract.
8. **Fix loop** — any failed gate returns to step 5.

## Output

Whatever `editorial-machine/SKILL.md` §Output contract requires for the chosen
lane, plus the page brief. Report the delivery URL you actually loaded.
