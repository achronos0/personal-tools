# A mechanism has to earn its place

**Trigger: I am about to add machinery.** A cache, an index, a pool, a retry, a queue, a memo, a
threshold, a tuning constant, a layer of indirection, a config knob. Anything whose justification is
"this will be faster / safer / more robust" rather than "this is the feature".

**Before writing it, answer: what does it buy, compared to not having it?** And be honest about
whether I know that or am assuming it.

Ky's framing, which is the useful taxonomy:

> "if I'm going to add a cache, does that help? Is it obvious (do it), a design decision (discuss
> it), or not needed (bin it)? Does it **need** measuring?"

Four outcomes, and the job is to work out which one I'm in **before** building:

| | |
| --- | --- |
| **Obvious win** | Build it. Say why it's obvious in a sentence, so a reader can disagree. |
| **Needs measuring** | Measure *first*. The measurement is cheaper than the mechanism plus the review plus the removal. |
| **Design decision** | Surface it — this is where `discuss-before-acting.md` takes over. |
| **Not needed** | Bin it. This is the outcome I systematically underweight. |

## The specific error: measure the baseline, not the artifact

**When adding X to avoid Y, the number that matters is Y.** I consistently measure X.

Worked instance. I added a per-request cache in front of some derived data, and when its unbounded
growth was questioned I measured, carefully and correctly, **how much memory each cached entry
held**. Good method, wrong subject: that is the cost of *having* the cache. I never measured what a
cache *miss* cost — the thing the cache exists to avoid. When I finally did, the answer was ~0.25 ms
against endpoints that make network round trips in the hundreds of milliseconds, and the decisive
figure was one I had not thought to take at all: **a cache *hit* already cost 0.131 ms**, because the
function it fronted deep-copied its result on every call regardless. The cache was buying ~0.12 ms.

The mechanism was deleted. Net −113 lines, and the entire memory-exposure question it had generated
evaporated with it, because nothing was retained any more.

**So: measure the thing you claim to improve on.** A measurement of the artifact tells you what it
costs, never whether it was worth building.

## The tell: a constant I cannot defend with a number

`64`. `~10`. `30s`. `3 retries`. If I am writing a number into the code or into a comment and I
cannot say what measurement produced it, I am guessing, and the guess will acquire authority by
sitting in the source where it looks like a decision. That is
`decisions-carry-their-constraints.md`'s inverse failure, arriving through a different door.

**A bound nobody measured is not a safety feature.** It is an unexamined constant that will fire one
day and produce behaviour nobody can attribute — Ky's phrasing when he refused my second answer:
*"maybe when we add the 9th flag and the LRU actually fires, the contention causes mass 'random'
slowdowns and nobody has a clue why."*

## The second failure: refining the answer instead of re-opening the question

I took three positions on the same mechanism — **document the risk**, then **bound it**, then
**delete it** — and each was a refinement of my previous answer rather than a return to the original
question. Ky had to ask "what does this buy us?" in three different wordings before I stopped
optimising the mechanism and asked whether it should exist.

**The tell is an escalating series of fixes to something whose premise was never checked.** Each step
felt like progress because it responded to the last objection. None of them touched the assumption
underneath. When I find myself on round three of improving a thing, that is the signal to go back to
whether the thing is needed, not to improve it better.

Note also that the first two answers were *both* responses to review pressure, and both were
shaped to satisfy the objection rather than to settle the question. Answering the critique is not the
same as answering the question.

## Why the existing rules do not cover this

Worth stating, because each one nearly does and none of them fires:

- **`hedges-are-a-trigger.md`** keys on *my own hedge* — "probably", "I'd expect", "assumed rather
  than verified". Here I was confidently wrong: I wrote a magnitude down as fact. **A confident
  assertion trips no hedge detector**, which makes this the more dangerous shape of the same error.
- **`evidence-and-claims.md`** is method — how to establish something properly once I have decided
  to. It does not supply the impetus to establish it, and its worked examples are reads of state
  that already exists, not forward-looking "will this help".
- **`discuss-before-acting.md`** would have caught it if I had classified "add a cache" as a
  judgement call, but its examples are naming, structure and scope, and its remedy is *discuss*. The
  missing step is earlier: deciding whether this needs discussing, measuring, or binning.
- **`scope-bias.md` pushed the wrong way.** Bounding the cache *felt* like the thorough option.

## The tension with `scope-bias.md`, stated so it doesn't get resolved by vibes

`scope-bias.md` says bias toward expanding scope, handle the edge cases, do it properly. This rule
says don't build machinery that hasn't earned its place. They only *look* like they conflict, and
Ky's distinction is the one that separates them cleanly:

- **scope-bias is about CAPABILITY** — what the thing can do. It is the operational form of
  `engineering-values.md`'s *"I prefer general solutions over specific ones"*: handle the case I was
  about to defer, support the shape I was about to exclude, build the general version.
- **this rule is about MECHANISM** — apparatus added for speed or safety that changes no capability.

**A cache makes the system do nothing it could not already do.** That is the test, and it is sharper
than "problem versus solution", because `engineering-values.md` explicitly *wants* powerful
internals — so "it's internal" cannot be the disqualifier. Note its three worked examples (one
property instead of a parallel operator set, one tool with modes instead of a script per target, a
DSL instead of bespoke SQL) are all capability choices: the complexity it pays for buys reach, not
speed.

So when the two seem to pull apart, ask what the extra work *adds*. New reach → scope-bias wins,
build it. Same reach, assumed cost → this rule wins, measure or bin it.

## How to apply

- Name the mechanism before writing it, in one sentence, with what it buys.
- If that sentence contains a number, know where the number came from.
- If it contains "should be faster" or "could grow unbounded", **that is the measurement to take**,
  and take it against the baseline, not the artifact.
- Prefer deleting to tuning. A mechanism that needs a constant to be safe is a mechanism to be
  suspicious of.
- Measuring is usually minutes. Building, reviewing, defending and removing is hours, spread across
  other people.
