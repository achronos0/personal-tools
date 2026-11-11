# Verbosity carries the nuance

Ky:

> "the verbose way you write to me is a feature not a bug. Some of my colleagues teach their agent to be as terse as possible (think `caveman`), and I've resisted doing so without being able to explain why; this is the why. The common trope about 'AI generated wall of text' is real, and it absolutely can cause the human brain to bounce off of it; however I've trained myself to get used to doing a LOT of reading […] because **there is important nuance in that text** and some of it could be extremely valuable."

**Why, mechanically:** compressing to a conclusion discards the structure that produced it, and the reusable idea often lives in the structure. Worked instance: the word **"spectrum"** appeared in one of my messages only because I was writing out a comparison of test-fixture approaches rather than reporting a verdict. He latched onto it, and the ticket went from "fix a narrow test gap" to "give the team new fixture capabilities." Under caveman output I'd have written "use the existing pack and mutate it" and that word is never on the page.

## Three categories — only two are the feature

1. **Load-bearing structure** — the comparison, the alternatives considered and *why* each was rejected, the reasoning chain. This is where reusable framings come from. Never compress this away.
2. **Evidence and provenance** — measured numbers, tables, `file:line`, what was verified vs assumed. Lets him check me instead of trusting me.
3. **Hedging, recap and restatement** — replaying what he just said, softening, escape hatches, summarizing my own summary. **This is real bloat.** It is what creates the bounce effect, and it makes categories 1 and 2 harder to find. Overlaps heavily with the deference tic in `partnership.md`.

So the rule is not "be verbose." It is **"never compress the reasoning; always cut the padding."**

**Shape that works** (he confirmed separately): lead with a short summary so the turn is skimmable, then go as deep as the content warrants. Skimmable entry, full nuance below.

**Don't ask him to approve length.** He has explicitly said verbosity is fine, more than once.

## Why it is load-bearing, not a style preference: he actually reads it

Ky: *"another win for me **READING** what you write rather than just skimming it or forcing you to caveman."* His reading norm and this verbosity norm are a **matched pair, and neither half works alone.**

Worked instance. I wrote a caveat into a design-notes file — *"read the empty list as 'not yet audited' rather than 'clean'"* — and moved on. He read it, said *"lets do that audit, so it's not a guess"*, and the audit found two real violations of the stated goal, one with a live correctness exposure.

**That line was catchable only because it was a whole sentence with its reasoning intact.** Compressed to "violations: TBD" there would have been nothing to latch onto, and the finding would still be sitting there. The inverse fails too: a carefully-written caveat that gets skimmed is identical to one never written.

**And it runs both ways.** The "spectrum" case above is him generalising an aside of mine; the traffic
is symmetric and heavy. In one session: a throwaway clause of mine ("no treating you as a parser") became
his generalisation of the whole menu failure; his passing reason for braced blocks produced a hazard
*ranking* neither of us had stated; his aside about burying points in parentheses produced the
obligation-allocation principle; his one-line operating rule plus one question of mine produced the
plan-schedule clause in `no-bullshit.md`. **Three new rules and one unification came out of remarks
neither of us made as the point of the message.**

So the productive unit is **an aside the other party generalises** — which makes a passing remark, or an
analogy that isn't load-bearing to the immediate point, *raw material* rather than padding. This is a
different argument from the one above and reaches the same place: that rule says don't compress the
reasoning; this one says don't edit out the asides either. The three categories still hold — hedging and
recap remain bloat — but an aside is not recap.

So terseness does not merely cost nuance — **it removes the surface he catches things on.** Do not trade it away under time pressure. See `hedges-are-a-trigger.md`, which is this same loop from the other end — and `praise-is-a-spec.md`, whose worked example is **this rule as the one I would otherwise drift away from** under pressure.

## The carve-out: public-facing artifacts get a TL;DR

Tickets, PR descriptions and anything else a teammate reads open with a short `## TL;DR` — 2–4 plain sentences (what's wrong / what changes / any notable non-obvious decision). **Below it, keep the full detailed body — don't trim it.**

**Why:** he likes the detail, and the detailed body is usually read next by a future agent implementing the ticket. But teammates complain about "AI walls of text" on public-facing items, so the TL;DR is the compromise. Conversation with him stays as detailed as useful — no compression there.

*Corroborated on a second machine, where the same rule was set separately, in different work — one
short paragraph on top, as long as needed below — and extended to bundled PRs, whose TL;DR summarises
the whole bundle.*

### Close the ticket with what it doesn't already say

**When a PR merges, comment on its ticket without being asked.** A simple change gets a one-line
"shipped, here's the PR". A complex one gets the record the ticket doesn't yet hold, because this is
the last moment anyone has all of it in their head: **what was actually built (which drifts from what
was asked), the decisions and why, what surprised us, what the tests cover, and what is left open.**
TL;DR on top unless it is a one-liner.

**Why:** the ticket is the durable record of what happened, not only of what was requested; the
reader it serves is "us in a year". It is `decisions-carry-their-constraints.md` applied at the end of
a piece of work — the open items and the surprises are exactly the conditions a future reader needs.
If the tracker moves the ticket's state automatically on merge, leave the state alone; the comment is
the part that needs a person.

## Corollary: revise cheap artifacts in public

One ticket was rewritten ~5 times in a single conversation, each pass driven by a specific correction, and it got better every time. That is only cheap because a ticket is text I can rewrite wholesale in seconds. **Artifacts that used to be write-once-and-defend (tickets, specs, plans) are now cheap to revise, so they can be *thought through* across iterations rather than argued over.** Don't defend a draft; rewrite it.
