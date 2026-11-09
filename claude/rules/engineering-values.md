# Ky's engineering values

In his words, unprompted:

> "I prefer general solutions over specific ones; I'm comfortable prioritizing power and flexibility over simple and cheap (sometimes to a fault), although I also like to strongly compartmentalize the resulting complexity behind simple-looking contracts; I am a huge believer in Root Cause Analysis, and I don't just mean in incident triage, I tend to focus on questions like 'how did this system come to be built this way' and use that to inform improvements (code refactoring, workflow changes, etc.)"

## 1. Lead with the general solution; let him scope down

The asymmetry favours it — proposing narrow and being expanded costs a round trip, while proposing
general and being trimmed is cheap, and he trims readily. **This is my most reliable failure mode
with him.** In a single session I proposed the narrow option three times and was corrected each time:

- **A test that asserts on generated output instead of real coverage.** A column could hold nulls in
  production, and no fixture contained one. Rather than get null-bearing data, I proposed asserting
  that the query builder *emitted* the right null-handling property. Ky asked what that would prove.
  Nothing: it restates a configuration literal through a compiler that was already tested. **The
  narrow option wasn't just smaller, it was vacuous** — see `test-data-and-coverage.md`.
- **Excluding the realistic half of a capability.** Asked to add fixture-shaping capability, I scoped
  it to fully hand-authored data and explicitly excluded anything derived from real production
  slices — on the reasoning that derived data can't produce arbitrary volume. That conflated
  "derived from real data" with the *one* derivation technique that can't create volume (in-place
  mutation). Replicating real rows with perturbed keys is both derived and volume-capable. He pushed
  back; he was right.
- **Fencing out the open-ended part as "not deliverable."** The ticket carried a genuinely
  open question — what testing approaches become possible once authoring test cases is no longer
  human labour. I proposed cutting it for having no definite deliverable. **The exploration was the
  value**; the narrow deliverables were the by-product.

## 2. State the cost honestly anyway

*The general form is `no-bullshit.md`: suppressing the price to
make a proposal land distorts what the reader will believe about the work.*

"Sometimes to a fault" is his own caveat, which means he wants the expense of the general solution
*surfaced*, not suppressed to make it palatable — and not used as a reason to propose the narrow
thing instead. Give him the general option with its real price tag and let him make the call.

## 3. The target shape is powerful internals behind a narrow contract

Not "simple all the way down", and not complexity leaking to callers. Three shapes he designed or
endorsed, with the narrow alternative each one beat:

- **One property instead of a parallel operator set.** An expression DSL needed to express that an
  arithmetic node might produce null. The obvious narrow fix was a null-safe variant of each existing
  operator — doubling the operator set, and leaving callers to pick the right twin. What shipped was
  a single required property on the existing node type, covering both single-operand and
  multi-operand operators, with no new operators at all. **One concept, declared once per node, in
  place of a combinatorial expansion.**
- **One tool with modes instead of a script per target.** Ad-hoc database investigation spanned five
  different targets — a local database, a service's own, one shard of a sharded fleet, a replica, and
  an analytics warehouse. The cheap path was a script per target, each with its own connection
  handling and output format. He wanted one CLI with five target modes behind one interface, so that
  learning it once covers every target and a query can be re-pointed by changing one argument.
- **A declarative DSL instead of hand-written queries.** Reports are defined as JSON expression
  trees compiled to SQL, rather than each report carrying bespoke SQL. The complexity moved into one
  compiler that gets tested once; report authors hold none of it.

**Predicts he'll dislike:** a bespoke script per use case, a narrow API that will need widening, an
abstraction that makes the caller hold the complexity, and any fix whose shape is "add another
variant alongside the existing ones."

## 4. Do the archaeology before proposing the change

"How did this come to be built this way" is a standing question, not just an incident-triage move —
and it applies to *processes and workflows*, not only code. It usually surfaces the constraint that
was real then, which is the actual justification for changing it now.

- **Worked example.** Test fixtures existed at exactly one point on a spectrum from real-data-derived
  to fully synthetic, and I was about to propose filling in the rest as though it had been an
  oversight. Asking why only one point was ever built produced the real answer: shaping data was
  per-case human labour that had to be redone *every time the fixture set was regenerated*, which
  made every point but the cheapest one economically impossible. That answer became the ticket's
  framing **and** generated a design bar — a shaping workflow must be cheap to re-run and cheap to
  re-read, or it hasn't cleared the threshold that made the original constraint real.
- **Second instance, same session.** An earlier audit had missed two genuinely suspect sites, and the
  tempting write-up was "the audit was incomplete." Asking why it missed them showed the heuristic
  keyed on *asymmetric* guarding — a site guarded inconsistently across branches looked wrong, while
  a site exposed symmetrically in every branch was invisible to it. **A finding about the rule, not
  about the lines**, and it changed what the next audit should look for.
- **Corollary he responded well to:** say **which** constraint changed, so the write-up reads as
  "correct call under different economics" rather than as criticism of the original design.

**The sharp version: a design decision encodes the cost structure at the time it was made.** When
that cost structure changes, re-open the decision instead of treating it as settled. His own framing:
*"modifying seed data to hand-craft specific cases was an unthinkable luxury when I invented the
system — with your help, it becomes entirely feasible."* The single-mechanism design was a correct
cost judgement, not an oversight.

**Stated generally, this is `decisions-carry-their-constraints.md`** — the archaeology rule is that
principle applied to design decisions specifically.

Related: `scope-bias.md`, `partnership.md`, `test-data-and-coverage.md`.
