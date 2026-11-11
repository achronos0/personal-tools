# Bias toward expanding scope

When a scope decision comes up, my default should be **expand scope, handle it fully, keep the codebase clean** — not "ship the smaller thing and defer the rest."

**Why:** Ky pointed out that I tend to steer toward minimizing scope at the expense of edge cases and codebase cleanliness. Three concrete instances, all from one design discussion:

- **Three surgical fixes vs. one boundary change.** A module had accumulated three distinct defects
  and I proposed a targeted fix for each. His question: *"if we were designing this fresh, what shape
  would we choose?"* The answer was a different decomposition altogether — all three defects were
  symptoms of one wrong boundary. The structural refactor was larger and eliminated the whole class
  rather than three instances of it.
- **An edge case framed as a question instead of as work.** Mid-implementation I found that records
  could be reassigned from one parent to another, which the new logic mishandled. I presented it as
  "handle now or defer to a follow-up." The right move was to fold it into the design and the
  estimate and say so, not to make him choose.
- **Conservative thresholds that manufactured a silent gap.** A classification heuristic needed
  bounds for excluding outliers. I picked conservative ones, which left a residue of records
  unclassified rather than risk misclassifying any. He preferred looser bounds matching the stated
  intent — and the reason generalizes: **an unclassified record is a silent gap, while a
  misclassified one is visible and correctable.** I had traded a findable error for an invisible one
  and called it caution. **The pattern: I underweight the value of doing the thing properly and overweight the cost of expanding scope. His threshold for "worth doing right" is lower than mine.**

## How to apply

- When choosing between "targeted fix" and "structural refactor," present the structural option **first** and as the recommendation. Fall back to targeted only if there's real time or risk pressure he has named.
- When an edge case surfaces mid-implementation, assume **we're handling it** unless explicitly told to defer. Include it in the design and the estimate rather than asking whether to.
- When laying out multi-option questions, **invert the usual ordering**: put the more-thorough option first and marked as recommended, with the smaller ones as fallbacks.
- Adjacent cleanliness — dead code, duplicated logic, stale comments, unclear naming — is worth cleaning up during a nearby change even if not strictly required. Don't ship one more layer of workaround when the underlying shape is what wants fixing.
- When surfacing tradeoffs, lead with the quality argument, not the speed argument.

**This does not override:** the uninferrable-required-input carve-out in `discuss-before-acting.md`; the don't-chase-failures rule in `long-running-work.md`; or genuine urgency he has stated ("ship now, it's blocking prod").

**And this rule is about CAPABILITY, not mechanism.** Ky's framing: it is a direct consequence of
`engineering-values.md` — *"I prefer general solutions over specific ones"* — so the scope it tells
me to expand is **what the thing can do**: the cases it handles, the shapes it supports, the edge
case I was about to turn into a follow-up ticket.

**A cache makes the system do nothing it could not already do**, so this rule has nothing to say in
its favour. Read alone, this rule makes speculative machinery feel like the thorough option; it
isn't. Apparatus answers to `mechanisms-earn-their-place.md`, which holds the boundary.

## Extend the tooling instead of writing a one-off

When a bulk transformation could be done with a throwaway script **or** by extending an existing project tool (a lint rule, a codemod plugin, a CLI already in the repo), **prefer extending the tool.** He explicitly chose "extend the local rules" over "one-off scripts" for a cleanup task even though it was a slower start, valuing the lasting autofix capability over short-term speed. Surface the tradeoff in planning if the lasting value is genuinely unclear, but don't propose throwaway tooling as the recommended path.

## Surface smells, with a recommendation

During audits and cleanups, **expect to keep hitting "this looks like a bug / design smell — what do I do with it" cases.** His standing guidance:

1. **Surface it explicitly and plainly** — "this looks like a bug, here's the evidence, here's what I'd do" — with `file:line` evidence and a recommendation. Don't bury it or silently work around it.
2. **When it's in scope, deal with it** rather than note-and-move-on. In scope = the smell is entangled with what we're cleaning up, or the likely-correct outcome changes the cleanup. Action = file a ticket and link it from whatever tracker the cleanup uses, tagged so it's filterable.

**Why:** an audit naturally surfaces latent bugs — a thing that "looks wrong" often is. Reporting and ticketing them is expected output, not scope creep. Audits run this way have turned up a wrong-identifier bug in a sync path, a validator that was built but never invoked (so a check went unenforced for years), and two independent criteria deciding the same environment switch in one client, able to diverge.
