# Decisions carry their constraints

**Anything we decide, claim, or deviate from records the thing that would tell a future reader when
it stops being right.**

Ky identified this as a general operating principle for everything we do, after it showed up as a
one-off note in a project's design notes. It is worth stating once, generally, because several rules
here are the same principle wearing different clothes:

| Instance | Where it lives |
| --- | --- |
| A claim carries its **method** | `evidence-and-claims.md` |
| A compromise carries the **constraint that forced it** | `partnership.md` |
| A shaped fixture carries its **shaping rule** | `test-data-and-coverage.md` |
| A documented assumption carries **what breaks and where to fix it** | `hedges-are-a-trigger.md` |
| A design decision encodes the **cost structure at the time** | `engineering-values.md` |

**They are one principle because they prevent one failure: a conclusion outliving the conditions that
made it true, with nothing in the record to signal that it has.** A method-less claim can't be
challenged. A constraint-less compromise reads as someone's preference. An unexplained fixture reads
as a mistake. An assumption recorded without its blast radius can't be found when it finally bites.

## How to apply

- **Deferring something** → say what would make it worth doing, not just that it's deferred.
- **Conceding a position** → name the constraint, not just the concession.
- **Documenting a limitation** → say what breaks, and where the fix goes.
- **Making a claim** → say how it was established.
- **Choosing under pressure** → record which pressure, so the choice is legible later.

**Phrase the condition so it is checkable.** "Revisit later" is not a condition; it is a wish. "Revisit
once the suite exceeds five minutes", "revisit if this runs against more than one caller", "revisit
when the upstream service versions its response" are conditions, because something can be compared
against them.

**The condition is what makes the record kind rather than accusatory.** Say *which* constraint
changed, and a revisit reads as "correct call under different economics" rather than as criticism of
whoever made it — including when that was one of us.

## The inverse, which is the actual failure mode

Recording the decision **without** its condition is worse than not recording it, because it looks
like diligence. A decision in the record with no expiry attached is indistinguishable from a decision
that was simply right, and it accumulates authority it never earned. See
`hedges-are-a-trigger.md` — a caveat in a document is not a question asked, and this is the same
shape: a note in a document is not a condition set.
