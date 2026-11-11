# Git discipline

## Commit as soon as it verifies

**Commit the moment a change verifies.** Do not hold working code uncommitted while building the next piece (tests, docs, a follow-up refactor) in order to land it as one tidy commit. **Extra commits are free; lost work is not.**

Ky: *"I'm really not passionate about having a pretty commit history: I do not mind if we create multiple commits for a single changeset, e.g. one for engine changes and a follow-up with some tests. I'd far rather that, than risk losing work."*

**Why:** I once had an implementation done and verified but uncommitted while writing its tests. To check the tests could actually fail, I mutated the implementation, then reverted the mutation with `git checkout -- <file>` — which restores from the index, so it discarded the whole uncommitted implementation, not just the mutation. Everything had to be replayed from the transcript. One `git commit` beforehand would have made the revert free and correct.

- Commit each piece the moment typecheck, lint and tests pass on it. "Engine change" then "its tests" is a perfectly good pair of commits.
- **Never `git checkout -- <file>` on a file with uncommitted work.** It reverts to the index, not to "before my last edit". To undo a deliberate mutation, reverse the specific edit, or commit (at minimum `git add`) first.
- Mutation-testing an implementation — a good habit — *requires* the implementation to be committed first, because the whole point is to damage and restore it.

## Layer commits foundation → application

When a single PR touches several files across architectural layers, split it into commits ordered from foundations to application, so a reviewer can read commit-by-commit and validate each layer before seeing how it composes upward. He asked for this explicitly: *"try to layer commits so we do the underlying pieces first"*, with the signal being "let me sanity-check each foundation before approving the application code that uses it."

Rough canonical order: schema/datasource additions → shared primitives → composite or derived pieces → the feature definitions that consume them → tests and fixtures → docs. Each commit should independently pass typecheck and lint, foundation commits should not import application code, and a change too small to stand alone folds **into** the next commit, never the reverse.

**Readability is the tie-breaker, not the priority.** Never hold verified work uncommitted to produce tidier layering — commit it and layer the *next* piece on top. The commit-early rule wins wherever the two pull in different directions.

**Honest history, not decorative splitting.** Layer commits only when the work really was self-contained and independently verifiable at each stage. If we implement-verify-commit in rounds, layer them. If the work happened as one intertwined push and only the tests came later, a two-commit "implementation → tests" split is honest; a manufactured three-way foundation/callers/cleanup split isn't, especially when the files span layers and can't be separated without hunk-picking. **Don't force artificial commits after the fact.**

## PR granularity follows the cost of landing a PR

Commits are free; **PRs are not, when each one carries a manual landing cost** — merge, wait for CI,
cut a release, promote it, deploy. On a second machine, one debugging push produced eight narrow PRs in
one repo and three in another, each needing that whole dance. In retrospect it should have been two or
three.

**So, under that condition, default to one PR per round of work, bundling unrelated fixes**, and split
only when:

- one change is **blocking a deploy** and the others aren't — ship the blocker alone, fast;
- one is **materially riskier** than the rest (a hot path beside a cleanup), so it deserves its own
  revert unit;
- the changes **span repos** — one PR per repo, still bundled within each.

Layering still applies *inside* the bundle: commits ordered foundation → application, so the reviewer
can read it commit by commit. A bundled PR's description opens with a TL;DR covering the whole bundle
(`verbosity-and-nuance.md`).

**The condition that made it true:** the reviewer was the same person who ran every release, and
already had full context from the session. **It reverses where review is shared** — several reviewers,
each owning part of the code, are better served by narrow PRs they can each take whole, and the
landing cost is spread across people rather than paid serially by one. Check which situation you are
in rather than carrying either default between projects.

## Merge vs rebase: published → merge, unpublished → rebase

Ky, after I rebased 23 commits onto a 4-commit drift on a PR that was already out for review: *"typically in this case I would have done a merge rather than a rebase. 23 commits is a lot of rebasing, and master wasn't that far behind."*

- **Published and a human has engaged** (reviewer assigned, comments left, review in progress) → **merge, always.** Not a judgement call.
- **Published but no human has touched it** → either. Rebase is fine if conflicts look shallow. **An automated review bot's round does not count as a human touch** — his explicit refinement: *"we care about human touches, I don't mind rebasing after e.g. after we've done a [bot] round, if it otherwise makes sense."* The bot marks its own prior review outdated when re-run, so its state is disposable. **But rebase after the bot's findings are *triaged*, not merely *produced*** — force-pushing while findings are unaddressed orphans the line anchors on the comments you still have to act against. Safe ordering: triage → reply → rebase.
- **Unpublished** → rebase freely. Private history, nobody's time but mine.

**Ratio check, as a second gate.** Commits-on-branch vs commits-on-trunk. 23 replayed to absorb 4 is a bad trade — 23 chances to go wrong to integrate 4 things. Small branch against large drift: rebase is cheap. Large branch against small drift: it isn't.

**The argument I got backwards.** I justified the rebase with: *squash-merge means this history never reaches the trunk, so the reviewer is its only consumer — keep it clean for them.* That is half an argument, and the other half reverses it. **If the history is disposable, don't pay any cost to keep it pretty** — especially not a cost borne by someone else. A force-push on a reviewed PR weakens or destroys "changes since you last reviewed", re-anchors or orphans existing comments, and leaves anyone mid-read on a branch that no longer exists. The aesthetic cost I was protecting is also smaller than I treated it: a merge commit doesn't destroy foundation → application layering; the layers stay in order with an integration commit among them.

**Not a differentiator:** verification cost. Either route lands the new trunk code in your files and owes the full targeted suite. Only replay risk and reviewer disruption actually differ, and both favour merge.

**The two real exceptions, where rebase isn't optional:**

1. **A stacked PR whose parent was squash-merged.** Merge actively fails — it drags the pre-squash duplicates back in. `rebase --onto` is the only correct tool. **This is where my bias came from: I generalised a narrow exception into a default.**
2. **Excising something from history** — a leaked secret, a bad commit. No alternative.

**Diagnostic before choosing** (this part was right and worth keeping): `git merge-tree $(git merge-base HEAD origin/master) HEAD origin/master` to see which files conflict, then `git log <base>..HEAD -- <those files>` to count how many of your commits touch them. Make a backup ref either way (`git branch -f backup/<name>-prerebase HEAD`). Note that the diagnostic informs the *cost*, not the *decision* — a published, human-reviewed branch merges even when the rebase would have been easy.

## All of our work goes through a pull request

Ky, stated as a general rule: **our changes always land through a pull request, even where branch
rules would let us push directly** (an integration branch others push to, an unprotected branch, a
repo with no review requirement).

**Why, in his words, in order:** reviewability and CI. Mainly, it **enforces discipline on both of
us: work goes out in changesets, each independently testable and reviewable.** In practice, the
pull request's changes page is his preferred way to review code I write. A pull request as the
shipping record (description, Testing section, ticket link) is a bonus, not the reason.

**This constrains us, not the repo.** A project may allow direct pushes for other people (a release
crew pushing an urgent fix to an integration branch, say), and documenting that is fine. It doesn't
change what we do.

## Every commit subject and PR title starts with its ticket

Ky's preference: **every commit subject and every PR title starts with its ticket key, in the form
`TICKET-NUM: Description`**, e.g. `<KEY>-123: Fix the knob offset`. That includes small follow-ups in
the same work (a formatting fix, a test tweak).

**Why (Ky): the key links a commit and its ticket both ways**, so history can answer both "which
ticket gave rise to this work?" and "what work did this ticket cause?". Without the key, both
questions go silent. I found the second one failing before I knew the reason: a command listing the
tickets waiting on an integration branch, by reading keys out of commit subjects, silently missed
two commits that named none. They were on the branch, and no ticket could find them.

**Documentation-only changes are the exception: don't manufacture a ticket for them.** Ky doesn't want
tickets created just to satisfy his own pattern. Instead, in order of preference:

1. **Let the docs ride along** with another pull request, when one is going out anyway.
2. **Reuse the ticket that gave rise to them**, whichever one it was.

**For other work with no ticket yet**, file one or ask, before the first commit, and take the key from
the tracker's response. Don't name a branch after a guessed number: I once named a branch for a ticket
I was about to file, and the real key was off by eight. This is the uninferrable-input carve-out in
`discuss-before-acting.md`, extended from branch and PR title to every commit.
