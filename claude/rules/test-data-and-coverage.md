# Test inputs and honest coverage

These were learned from data-heavy work, but almost none of them depend on the inputs being rows.
Read "fixture" as any fabricated test input: a data row, a recorded API response, a mock, a stub, a
story, a selector. Where a claim really is data-specific, it says so.

## The silent-failure principle

**Test scaffolding fails toward "nothing happened," and "nothing happened" is indistinguishable
from a pass.**

- A fabricated row with one wrong key → empty join → green.
- A mock whose URL doesn't match the request → never fires → the test exercises a fallback → green.
- A selector that matches nothing → an assertion on an empty collection → green.
- An empty lookup table behind a `LEFT JOIN` → one silent null row → pinned green by a snapshot.
- A read whose pattern can't match the file's syntax → "it isn't there."

**Every one of these is the same bug**, and it is the same bug as the vacuous read in
`evidence-and-claims.md`: an empty result that reads as an answer, with no error raised. **Treat a
suspiciously empty result as a question about the method, not as data.** The remedy is always the
same shape: before trusting a green test or an empty result, establish that it *could* have come out
differently — mutation for a test, a positive control for a read, a deliberately-failing assertion
for a new fixture.

## A test is done when a mutant has failed it

The silent-failure principle as a **definition of done**, set as a standing rule on a second machine
after a feature shipped with nine green end-to-end tests and no evidence any of them could fail:

- **Name the mutant** each new or changed test should catch — the specific breakage of the code it
  guards, not "if it's wrong".
- **Run the mutant, watch the test fail, restore.** Commit before mutating (`git-discipline.md`), or
  restore from a copy with a non-interactive copy (`shell-environment.md`).
- **Run it against a fresh build.** A test harness that reuses an already-running dev server tests the
  server's *old* code, so the mutant never takes effect and the result says nothing about the test.
  This is the silent-failure principle striking the check itself.
- **Fix or delete** any test a relevant mutant doesn't fail. A test that can't fail is not partial
  coverage; it is a false statement about coverage.
- **Report which mutant each test catches** in the PR description, so the reviewer sees the evidence
  rather than the claim.

**Why it is a definition rather than a habit:** the person doing manual QA is relying on the suite. A
green suite that can't fail transfers their confidence to nothing.

## Invent only what the case requires

**Minimum fabrication is minimum audit burden.** Every fabricated element is a place the test can
disconnect from the system under test without saying so. Every element you *don't* fabricate cannot
fail that way.

This is why the realistic end of the spectrum below is preferred wherever it reaches: not because
real inputs are sacred, but because they carry fewer unjustified assumptions per unit of coverage.

## "Synthetic" means shaped, not invented from nothing

These are a **spectrum**, and recorded reality is a legitimate starting point at every step but the
last:

1. **Mutate** — take real captured inputs and change named fields (null a column, change a status code).
2. **Amplify** — replicate real inputs with perturbed keys, giving arbitrary volume from real
   distributions. *(Most data-specific rung; weak analogue elsewhere.)*
3. **Extend** — append crafted inputs to a real base.
4. **Fully synthetic** — authored from the schema or the type.

**Don't equate "start from real data" with the one technique that can't create volume.** I made
exactly that error — treated the whole category as in-place mutation only, and wrote it off when a
case needed volume. Amplification is derived from reality *and* volume-capable.

**The precondition varies even though the principle doesn't.** The realistic half of this spectrum
only exists where there is recorded reality to draw on. A greenfield API or an unbuilt component has
nothing on the left, and starts fully synthetic by necessity rather than by choice.

## A default is not a constraint

"Our fixtures come from recorded reality" is a **default with a known blind spot**, not a rule that
forbids a fabricated one. A sample covers only what it happens to contain, and **rare-but-real
states are rare by nature — so they are not reachable by sampling harder.** That is epistemology,
not a property of databases: recorded traffic will never contain the mid-pagination failure, and
recorded sessions will never contain the pathological input length.

So when coverage for a *named* edge state is missing, the question is **"what is the narrowest
mechanism for this?"** — not "can I find a real slice that happens to contain it?" and not "is
fabricated test input allowed here?" It is.

## The trilemma

Test inputs can be **specific**, **voluminous**, or **cheap to author** — pick two.

| Approach | Specific | Voluminous | Cheap to author |
| --- | --- | --- | --- |
| Hand-crafted cases | ✓ | ✗ | ✗ |
| Generative (property-based, fuzz) | ✗ | ✓ | ✓ |
| Recorded reality | ✓ | ✓ | ✗ to *shape* — you take what it contains |

Agentic authoring collapses it: a scenario described in intent can be instantiated faithfully, at
scale, documented, and re-applied after a regeneration. Use this framing rather than the stronger
claim that hand-authoring was ever universal — property-based testing and fuzzing exist precisely to
escape it, and a reviewer who knows them will say so.

**Its force scales with input-space cardinality.** For a large data space "pick two" bites hard. For
a component with a dozen meaningful states, hand-crafting all of them is feasible and the trilemma
dissolves. Don't import the urgency into a domain whose input space is small.

## A shaped input carries its rule

This rule's instance of `decisions-carry-their-constraints.md`. Any fixture that deviates from reality must record, next to itself, **which values are shaped, on
which inputs, and why that reflects something real.** Otherwise a future reader cannot tell
deliberate shaping from a mistake, and it becomes exactly the vacuous fixture set that starting from
real data was meant to avoid. Same principle as stating the method with a claim.

**Recorded inputs rot, and data slices mostly don't.** A real data slice stays representative; a
recorded response from an upstream service is representative only of a past version of someone
else's system, and silently stops being true. The realistic end needs no justification for data and
needs an expiry note for mocks.

## Don't paper a gap with fake coverage

**The most portable rule here.** Don't write a test that *looks* like coverage over a gap it doesn't
actually close. **Worked instance:** a column could hold nulls in production, and no fixture
contained one. Rather than get null-bearing data, I proposed asserting that the query builder
*emitted* the right null-handling property, as a "cheap equivalent" to running against the real
shapes. Ky asked what that would prove. Nothing — it restated a configuration literal through a
compiler that was already tested. The same theatre: asserting a mock
was called with the right arguments instead of testing the integration, or snapshotting rendered
markup instead of asserting behaviour.

**Prefer saying plainly: "this is uncovered, here's why, here's the ticket."** An honest gap is
worth more than a green test that hides it.
