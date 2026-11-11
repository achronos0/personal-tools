# Long-running work

## Always background a run over ~60s

**Run any suite or job expected to take more than ~60s in the background.** Never block the conversation on one. Ky: *"sometimes I might not care, but sometimes it wastes precious minutes."*

**Do not gate this on whether *I* have tree-free work left.** My first version of this rule said "if the only remaining work would touch the tree, just run it in the foreground." He corrected that: *"even when there's nothing you know of to be done that doesn't require the tree, I think backgrounding tests is the right call — it leaves us free to discuss other things, such as begin preparing for the next round of work. [...] odds are we can usefully occupy those minutes."*

**The time is ours, not just mine.** Backgrounding keeps the conversation open for planning the next piece of work, triaging review feedback, or anything else — even when my own queue is empty. Blocking the terminal spends his minutes to save me a little bookkeeping.

## The duty that comes with it: track the run, protect the tree

- Hold a clear note of what is running and against which commit.
- Make no edits, no `git checkout`, no second suite while it runs.
- If the conversation turns toward something that *would* change the tree, say so and offer the choice: stop the run now and re-run after, or finish the discussion first. **Never silently edit underneath a running suite** — the result would describe code that no longer exists.
- When it finishes, report the result against what was actually running.

**Judge the result by the summary line, never an exit code.** A piped command returns the pipe's status, so `<test command> | tail` reports 0 for a failing run. I made exactly that mistake and reported a red run as "passed clean".

**Killing a run has a cost.** Stopping a test runner mid-flight can leave orphaned workers and database connections; the next run may be much slower and fail in unrelated places. If a run was stopped, suspect contention before believing a new failure.

## Scope the run to the blast radius

Ky: *"we don't need to run the entire [suite] after every addition in this ticket — targeted runs are ok with me, if we screw up we will still find out before we ship"*

I was running a full ~3.5-minute suite after every increment of one ticket, including increments confined to a file nothing consumed yet. **CI is the backstop; a local full run per commit buys very little and costs minutes each time.** The line to draw is **what the change can reach**:

- **Touched shared engine code** — a core module, or a primitive every feature uses → **full suite.** It can break anything, and the blast radius is not visible from the diff.
- **Change confined to one feature's own files**, which nothing else consumes yet → **targeted run** of that feature's tests, plus typecheck and lint.

**Typecheck matters more than it looks in the targeted case:** a test runner that strips types without checking them will let a test file pass green with a type error in it. I shipped a wrong option shape once and only the typechecker caught it.

## Don't re-run a long suite chasing a failure name

When a run reports e.g. "1 failed, 182 passed" but my output filtering doesn't surface the failing test name, do **not** keep re-running trying to capture it. Long suites cost minutes, and repeated runs are irritating.

**Why:** after one change, a suite reported 1 failure in the summary but my search of the captured output came back empty. I tried to re-run with a tee'd log; Ky interrupted — *"the tests pass, I'm not sure why you had to run them multiple times"*. The summary line was a transient reading, and he already knew the suite was clean.

- If the count was clean before the change and the change is small and localized, trust that and **ask before another full run**.
- If a search against a captured log finds no failure marker but the summary claims a failure, the likelier explanation is that the name is in a chunk I didn't capture — not that there's a hidden failure. Ask; don't rerun to chase it.
- Prefer one targeted run over repeated full ones. If a specific file is suspect, run that file directly.

## Run an independent investigation alongside the work, not before it

Ky, after it paid off: *"good call on the fork+worktree for the search, that saved us precious time."*

**The shape:** an urgent change was ready to build, and one question about it — *can this ambiguity
actually fire on real data?* — needed a search harness over the real code and a copy of the data.
The answer could change the write-up but not the code, which had a sensible default either way. So
the search went to a forked agent **in its own git worktree**, and the implementation went ahead in
the main checkout at the same time. The search finished while the tests were being written, and its
numbers went straight into the PR description and the ticket.

**When it applies — all three, or don't:**

- **Independent:** the investigation's answer doesn't gate the next edit. If it would change what I
  build, it isn't parallel work; it's the first step.
- **Its output lands in a record**, not in the code under edit — a PR description, a ticket comment,
  a decision for a person.
- **It would otherwise block** — run serially, it is minutes of the person's time spent waiting.
  This is the same argument as backgrounding a suite: the time is ours.

**Why a worktree and not just a background agent in the same checkout:** a search harness is
scratch code that has to live inside the module to call its internals. In the shared checkout it is
an uncommitted file under my edits, at risk of being committed, swept up by `git add -A`, or
compiled into my test runs. A worktree on a detached HEAD makes it impossible to tangle.

**What a worktree does NOT isolate, which is the half that nearly bit:** it separates *files*, not
*shared services*. In that session the test package's setup dropped and recreated a shared test
database and flushed a shared Redis on every run — so the fork's scratch runs and my integration
tests would have reset each other's state, even from separate trees. I held my database tests until
the fork finished, and the fork's own first attempt did leave the template database half-built.
**Before running two things in parallel, ask what they touch outside the tree:** databases,
ports, caches, queues, a dev server, an external rate limit. Either give each its own, or
serialise just the part that shares.

**Brief the fork with the collision risks, not just the question.** "Work only in this worktree,
never touch the main checkout, read-only against the data, no external calls" kept it safe; I
missed the shared test database in the brief and caught it only by checking the package's test
setup before my own run. That check belongs in the brief next time.
