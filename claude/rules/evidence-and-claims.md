# Grep locates; it cannot claim

Ky, after I put two wrong grep-derived findings into a shared ticket:

> "*building code is now ~free*. Want to check which tables have which columns, based on a SQL dump text file? You could grep, but it's error prone; or you could just create it and query; takes an extra second or two but is correct-by-construction, risk of extra turns or blind alleys is zero. Same for TypeScript […] grep is error-prone, ASTs are expensive, a script that examines a runtime is seconds. […] my gut feeling is we waste more time on wrong reads than on wrong writes."

**Session evidence supports the gut:** ~5 costly wrong *reads* that session, **0** costly wrong writes.

## The rule: am I LOCATING or CLAIMING?

- **Locating** ("where is X mentioned") → grep, then read the hit. The read is the verification. Fast and correct.
- **Claiming** — a **count**, an **exhaustive list**, or **"this doesn't exist"** → **grep is not evidence.** Counts and absences assert completeness, and a regex cannot deliver completeness over a language it doesn't parse. Materialize and query instead.

## Tool order for a claim

1. **The runtime** — cheapest *and* most accurate. Config objects, registries and constant tables are just values: run a script that imports the real module and walks the actual objects. Sees post-evaluation truth (template literals resolved, spreads applied, computed keys materialized) that an AST walk would miss.
2. **Materialize into a queryable store** — pipe a dump into scratch SQLite/Postgres and query it; parse with a real parser. Correct by construction.
3. **A parser / AST** — when 1 and 2 don't fit.
4. **Grep** — for locating only.

**Editing stays string-based and that's fine.** Parsing source and printing it back yields the printer's formatting, turning a 3-line change into an unreviewable diff. The problem is reads, not writes.

## Why the read/write asymmetry exists (not luck)

**Writes are gated by construction:** an exact-match edit errors if the target moved; typecheck, lint and tests gate the result; `git diff` shows exactly what changed. *A wrong write announces itself.*

**Reads have no gate.** A grep finding nothing because the pattern is wrong is byte-identical to one finding nothing because the thing isn't there.

→ **A zero-result read needs a positive control.** Before trusting "no matches," prove the pattern can match something known to be present. (The failure: I grepped for `schema.table_name` against dumps that write `"schema"."table_name"`, got 0, and reported the table absent. Grepping a table I *knew* was there would have exposed it in 5 seconds instead of two ticket revisions.)

**And the control has to be the shape you are worried about.** A positive control proves the pattern
can match *the thing it matched* — nothing more. Controlling with a case you already know is fine
proves only that the search runs. Three times in one session I ran a valid pattern that was too narrow
for the question and read its clean zero as an answer: requiring spaces around `=` in a
`field = value` search; excluding hyphens from a `[[link]]` pattern when the links at risk were
hyphenated; and a plural typo in a quoted phrase. **None was a syntax error** — a syntax error
announces itself and self-corrects, whereas a too-narrow pattern returns a tidy zero that reads as a
finding. So before trusting a null result, ask what *variant* would break the pattern, and control on
that: the spacing, the hyphen, the quoting, the plural.

**The human advantage here is a prior about the expected count.** A person usually notices a
suspicious zero because they expected roughly N hits. I tend to accept the count, so the control has
to do the work the intuition would.

**The narrowing can be in the tool, not the pattern.** Claude Code's shell defines its own `grep`
function, which runs ugrep with `--ignore-files` — it **honours `.gitignore`**. In a repo that keeps
other checkouts in a gitignored directory, `grep -rl <symbol> --include='*.go' .` from the root
returned **0**; `command grep` returned **4**; the same wrapper run from inside the nested checkout
returned 4. Nothing about the pattern was wrong, and nothing in the output says files were skipped.
So: **a zero from a recursive search near gitignored content is controlled with `command grep`, or by
searching from inside the directory.** ripgrep, and tools built on it, also skip ignored files by
default; check what a search tool skips before trusting its silence.

## A documented contract is still inference — generate the artifact

A third source of false claims, alongside grep and stale references: reasoning from a documented rule instead of from the output.

I read that a config had no aggregation set on any field, applied the documented rule *"aggregation null → field joins the GROUP BY"*, and concluded the generated SQL collapsed distinct rows into an under-count. I was about to file it as a divergence. **Running the project's SQL generator printed the real query: no `GROUP BY` anywhere.** The rule governs *which* fields join a GROUP BY; with zero aggregating fields none is emitted at all. The contract was right and my application of it was wrong, which a contract can never tell you.

**Rule:** when the question is "what does this code actually produce", and a generator exists, **run the generator**. One command, and it is dispositive where a type-level argument never is.

**Note what went right there:** the bug was framed as a hypothesis needing confirmation, not reported as a finding, so the cost was ~10 minutes rather than a false entry in a ticket other people read. **Structural reads are hypotheses. Say so, then go and measure.**

## A positive control proves the PREDICATE, not the GROUPING KEY

I measured "how many entities are affected" with `COUNT(DISTINCT fk)` off a fact table. **That key is version-scoped** — one real-world entity has a key per slowly-changing revision — so I counted *revisions* and called them entities: 373 where the truth was 345, and worse, "13 over 10%" where the truth was **6**, because splitting one entity across its keys manufactures small-denominator fragments with extreme ratios.

The measurement was otherwise careful. It had a positive control on its zero. **The control proved the predicate could match; it said nothing about whether the grouping key meant what I assumed.** Falsifiability has to cover the *question*, not just the filter:

- Does the **predicate** select the right rows? → positive control.
- Does the **grouping key** identify the right entity? → check the key's cardinality against something known. `SELECT COUNT(*), COUNT(DISTINCT key), COUNT(DISTINCT natural_id) FROM dim_table` would have exposed it instantly.
- Does the **aggregate** answer the question asked? → `> 0` and `<> 0` differ: 97 vs 345 in that case, because negative adjustments make a year's sum net negative. Say which one a number means.

→ **A wrong number is more dangerous than a missing one**, because it survives review looking like evidence. That one reached a ticket before it was caught, and only because a *different* query returned a count that couldn't be reconciled with it. **Prefer measurements that can be cross-checked two ways.**

## Trace the value, not the expression that describes it

Across one comparison project Ky challenged six of my claims. **All six were wrong, and not one of the wrong things was a number that came from a query.** Every figure measured against the data survived; the prose describing *why* kept failing. A measurement answers a narrow question against real data and is either right or obviously broken; a mechanism sentence is a chain of inferences, and one weak link produces a confident, plausible, wrong claim that survives until somebody opens the file.

1. **Trace the value to where it is projected, not just the expression.** One field evaluated to a full allowance in an edge case — and was never used downstream. Reading an expression is not the same as following its output.
2. **Model BOTH sides from code.** The side I read from source was right every time. The side I modelled from item descriptions was wrong three times, including a missing guard and a date-attribution difference that *reversed a finding's sign*.
3. **Build the contradiction check into the query.** "A ≥ B by construction" was stated as an assumption and then returned as a column — `rows_where_B_higher = 286` is what exposed the reversal. **A sanity column that *should* be zero is worth more than a paragraph of reasoning.**
4. **An inherited assertion counts as unmeasured.** Two items carried "never observed in production data" from earlier work. Both were false when measured. Nobody had looked.
5. **Don't rank by how alarming a mechanism reads.** Code-level severity was a poor predictor of impact in both directions.
6. **Measure the *outcome*, not the *trigger*.** "How often does an input vary" (4.69%) answered a different question than "how often does the result differ" (1.54%).

### Learn what a producer sends from the producer, never from your own copy

A second machine, a different codebase, the same lesson. A service had been ingesting measurements
from an upstream for two years, and everyone — Ky and I included — treated that intake as settled
because it was old and quiet. It had been **silently dropping most of what the upstream sent**: a
name filter in the ingestion loop kept the fields it recognised and discarded the rest, and nothing
downstream could tell. Three wrong claims came out of one investigation before that was found:

- **Inferring the upstream from our own stored data.** I wrote into a ticket that the upstream "doesn't
  produce" a field, because our database never held it. **Our database is downstream of the filter
  that dropped it** — the one place that question can never be answered. What a producer sends is
  learned from the producer's code, or from raw payloads and logs captured before our code touches
  them.
- **Claiming impact without reading the consumer.** I said zero values from failed measurements broke
  a downstream rule. The rule already skipped zeros. One file read would have stopped the claim.
- **Treating age as evidence.** "Settled" meant "unexamined". **Old, quiet code has passed no test
  that new code hasn't; it has only gone unobserved for longer.**

**How to apply:** when something downstream looks wrong, walk the data path **from the producer
inward**, reading the code at each hop, not outward from where the symptom showed up. At each hop,
look for the **silent-drop shapes**: a `continue` in an ingestion loop, a lookup that skips unknown
keys, an error downgraded to a warning that nothing alerts on. And before a conclusion goes into a
ticket, verify it at its source — the consumer for an impact claim, the producer for a "what arrives"
claim.

This is "model BOTH sides from code" above, applied across a system boundary. How much to distrust a
*particular* codebase is a judgement about that codebase and belongs in its own notes; the method is
general.

**Comments count as prose.** I once took a code comment's word that an endpoint returned 403 without opening the file; it was the frontend rendering its own error page. A comment is *more* persuasive than a grep hit because it reads like a conclusion someone already reached.

## A read IS a one-off unit test

Not an analogy — the same kind of object: **a probe with a pass/fail output, aimed at a system too big to inspect directly.** Every probe fails the same way: it reports "nothing wrong" either because nothing is wrong, or because it never touched the thing.

| | Vacuous test | Vacuous read |
| --- | --- | --- |
| Claim | "this behaviour is correct" | "this thing isn't there" |
| Why it can't fail | snapshot pins whatever comes out | pattern can't match the file's syntax |
| Remedy | mutation testing — prove it *can* fail | positive control — prove the pattern *can* match |

So **the positive control is mutation testing in miniature.** Before trusting a read, ask the test question: *could this have come out differently if my claim were false?*

### A vacuous read is worse than a vacuous test — Ky's sharpening

> "A vacuous test in the repo misleads on how safe a code change is. A vacuous research read from us causes the test to not get written, and maybe even the code that it should have tested."

**A vacuous test is a false negative about a thing that exists. A vacuous read is a false negative about a thing's *existence*.**

- The first leaves **reality as a backstop** — the code still runs and can still be found wrong by a customer, a dashboard, a reviewer, another test.
- The second **forecloses the branch**: no ticket, no test, no code — *and no artifact that could later be discovered wrong*. **The error is self-sealing: you cannot get evidence against a question you stopped asking.**

**Proof from that same session:** one real bug ticket exists only because a grep happened to match — a search for three names hit, and the trail led to a snapshot test pinning the wrong output. The *adjacent* search, against schema dumps, used a bad pattern and returned zero. Same session, same kind of pattern, same kind of file. Had the matching side also used quoted identifiers, I'd have concluded "nothing reads these" and moved on — vacuous test still green, bug not *undetected* but **unconceived**. A quoting convention in a regex was the difference between that ticket existing and not.

**The remedy must differ in kind.** Mutation testing works on a vacuous test because the test exists and can be perturbed. A foreclosed branch has nothing to perturb, so the only intervention point is **the moment of concluding absence**:

1. **"I found nothing" is the HIGHEST-scrutiny result, not the cheapest.** The instinct is backwards — a null result feels like a fast clean answer. It should cost more work, not less.
2. **The positive control becomes mandatory, not advisable** — this is the case with no second chance.
3. **Say "method M found nothing", never "there is nothing."** Stating the method is what *keeps the branch alive*, not merely what makes it auditable. "There is nothing" closes the question; "my grep found nothing" invites "did you grep right?" — which is exactly the challenge that recovered this one.

**State the method with the claim** — this rule's instance of `decisions-carry-their-constraints.md`. When a read's output lands in a durable artifact (a ticket, a commit message, a project doc, a claim to Ky), say how it was made. "26,368 rows across 13 packs, queried from the SQLite directly" is auditable. "The table isn't in the dump" is a bare assertion wearing a finding's clothes.

**Reject a technique for *this case*, not in general.** When ruling an approach out, say which
property of **this** case rules it out, so the write-up doesn't teach a future reader a rule that
isn't true. I once wrote off hunting real data for a fixture outright; the correction was that it
was the wrong shape *there* only because that case needed a rare combination across ~60 columns and
no single real slice is that unicorn. Same move as saying "method M found nothing" — name the scope
of the negative, or it closes a question it had no business closing.

**Don't overstate what the check established.** *(A case of `no-bullshit.md`: an inflated method is a
materially untrue statement about our own work.)* Stating the method is half of it; stating it
*accurately* is the other half, and the failure mode is upgrading a weaker result into a stronger one
while writing it down — "unverified" becoming "measured", "present in substance" becoming "present
verbatim", "worked once" becoming "works". It is especially likely during a **cleanup or a summary**,
where the act of tidying invites rounding a hedge off to a conclusion.

Two instances in one day, both caught by a reviewer rather than by me: I recorded a cause as
unverified, then "corrected" it to the opposite claim under a heading reading *measured facts*, having
measured neither; and I claimed a structural diff showed every element present verbatim when what it
showed was every element present in substance. **The conclusions survived both times, which is exactly
why this is dangerous** — an inflated method reads as corroboration and nothing in the text flags it.
So: name the weakest step the claim actually rests on, not the strongest step nearby.

**Ties to `verbosity-and-nuance.md`:** compressing a *negative* finding to its conclusion strips its only error-correction mechanism. For positive findings the reasoning is valuable; for negative findings it is load-bearing.

## The probe answers "what WOULD be true", not only "what IS true"

*Which number to measure — the cost avoided, not the cost of the thing added — is
`mechanisms-earn-their-place.md` ("measure the baseline, not the artifact").*

Everything above is about interrogating **what exists** — which columns a table has, what SQL the
generator emits. The same economics apply to a **design** question, and that is the case I do not
reach for unprompted: *what would this cost? is this worth building? which of two shapes is
cheaper?*

Those are answerable the same way and just as cheaply. In the session behind this rule the probes
were ~20 lines of `node --expose-gc -e` and ~25 lines of `hrtime` benchmark, neither committed,
under a minute each. One of them deleted a feature.

**The scoreboard from that session is the argument.** Four claims reasoned to, four wrong: a module
cycle that did not exist, a cost that ignored 88% of itself, a bound described as safe that was
134 MB, a worst case reported as typical. Four things measured, four right, two of them
cross-checked two ways. **Not one reasoned magnitude survived, and not one measured one failed.**

So when a decision turns on a number — and "is this mechanism worth it" always does — the probe is
not a last resort before guessing. It is cheaper than the guess, because the guess costs the
build, the review, and the removal.

## The habit to break

The **container format** was driving my tool choice, not the question. In one session I queried structured fixture data correctly with real SQL over SQLite (26,368 rows, 0 nulls in the column of interest, 61 of 360 columns populated — trustworthy because queried), then hit *schema dumps* — same kind of structured data, arriving as text — and grepped. **Data arrives queryable → I query it. Data arrives as text → I grep it, even though text→queryable is now nearly free.**

**A grep's zero, an empty join and a fixture with one wrong key are one failure class** — an empty
result that reads as an answer. It is stated once, with the remedy, as the silent-failure principle
in `test-data-and-coverage.md`.
