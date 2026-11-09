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
