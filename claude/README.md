# Claude Code configuration

Portable, machine-independent configuration for working with Claude Code. Cloned and symlinked on
each machine so the same collaboration norms apply everywhere, and so a rule learned on one machine
reaches the others through git.

## Layout

- `rules/` — global instruction files. Claude Code loads every `*.md` in `~/.claude/rules/`
  automatically, in every session, in every project, **unless** the file has `paths:` frontmatter,
  in which case it loads only when a matching file is read (see **Writing a rule**). No
  configuration needed: the directory's presence is the wiring.
- `rationale/` — the evidence trail and history behind a rule: how it was found, why it is needed,
  what it replaced. **Never loaded at session start.** Each file is named after its rule, and the
  rule points at it in its first lines; the pointer is the only way to find it.

This README lives *outside* `rules/` on purpose — anything inside that directory is loaded into
context on every single session, so it holds only content meant for Claude to act on.

## What belongs here, and what doesn't

**Belongs here:** how Ky and Claude work together, how Claude should respond, how to think about
work, general engineering values, language-level style preferences, machine/shell environment facts.

**Does not belong here:** anything specific to a project or repository — that goes in project memory
or the repo's own `AGENTS.md` / `CLAUDE.md`. And **nothing employer-related whatsoever**: no code,
system names, ticket keys, data, metrics, or internal process. Worked examples in these files are
deliberately de-identified; keep it that way when editing.

## Org-agnostic, and keeping it that way is the writer's job

Ky's machines belong to **different employers**, and every file in `rules/` loads on all of them. So
this is not a privacy nicety: a worked example carried verbatim from one machine puts that employer's
systems into the context of a machine that belongs to another. Ky's instruction, set when the second
machine was onboarded:

> This repo must be org-agnostic and contain only general principles; it's on you to make that happen
> in your updates.

**"On you" means whoever is writing — Claude, on whichever machine.** Ky's read of the diff is a
backstop, not the scrub. A rule that arrives here un-generalised has already failed, even if review
catches it.

### Why this is hard rather than mechanical

The rules are only useful because of their worked examples, and **the examples are where the
identifiers live.** There are two ways to get it wrong, and they pull in opposite directions:

- **Keep the example verbatim** → the leak.
- **Strip it to the bare principle** → the failure `rules/verbosity-and-nuance.md` describes: a rule
  compressed to its conclusion loses the structure that makes it actionable, and nobody can apply it.

The target is **generic but concrete**: keep the *shape* of what happened — the sequence of mistakes,
the mechanism, the counts, the measured before/after — and replace the nouns.

### How, in practice

- **Name roles, not systems.** "An upstream service", "the identity provider", "the ticket tracker",
  "a sharded fleet" — not product, service, repo, table or field names.
- **Keep numbers that carry the lesson and identify nothing** ("8 narrow PRs where 2–3 would do",
  "0 hits against 4"). Drop ticket keys, PR numbers, hostnames, account ids, user ids and emails.
- **Separate the method from the verdict.** "Distrust *this* codebase" is a judgement about one
  codebase and stays in that project's memory; "learn what a producer sends from the producer" is the
  method, and comes here.
- **Write "on a second machine" or "in other work"** where provenance matters, rather than naming the
  project.
- **Commit metadata is content too.** Author and committer emails are part of this repo; set this
  repo's `user.email` to a personal address on every machine
  (`git -C <clone> config user.email <personal address>`).

### The same standard applies to any channel between machines

If the sessions on two machines talk to each other directly — peer messaging, a shared doc, a relayed
note — **that channel carries only what this repo could carry.** No org-specific example crosses it,
even as context for a question; write the question the way the rule would be written. (Today the only
channel is this repo — see **Git is the only cross-machine channel** below.)

---

# Onboarding a machine

**Read this whole section before touching `~/.claude/rules`.** Installing is the easy half. The
machine you are onboarding has its own accumulated rules and project memory, and some of it is
probably better than what is in here. **Do not assume this repo is authoritative over what a machine
already knows.** The symlink step is destructive to anything already in `~/.claude/rules`, so
reconciliation comes *first*.

## Step 1 — clone

```sh
git clone git@github.com:achronos0/personal-tools.git ~/dev/personal-tools
```

## Step 2 — inventory what this machine already has

```sh
ls -la ~/.claude/rules/                    # existing global rules
ls -la ~/.claude/projects/*/memory/        # per-project memory, one dir per project
```

**Do not trust an index file.** List the actual files and count them. On the machine this repo was
built from, the memory index implied a curated set while the directory held 139 files, and roughly
16 of those were about collaboration rather than project mechanics.

## Step 3 — classify every candidate

For each existing rule and memory file, decide: **discard, adapt, or merge.**

- **Discard** — it is about a specific project, repo, dataset, or employer tooling. It stays where it
  is (project memory) or goes away. It does not come here.
- **Adapt** — there is a generic principle inside, wrapped in specific examples. Rewrite it. Note
  that a scan for identifiers measures *contamination*, not *work*: the identifiers are usually
  inside the worked examples, and the worked examples are the load-bearing part. Re-express them
  generically-but-concretely. Stripping them to a bare principle is the failure mode
  `verbosity-and-nuance.md` warns about — a rule compressed to its conclusion loses the structure
  that makes it actionable.
- **Merge** — this repo already has a rule covering it. **Reconcile the two rather than keeping
  whichever arrived first.** Two machines may have learned the same lesson from different failures;
  the second instance is corroborating evidence, not duplication, and often has the sharper worked
  example. Keep the better one, or both if they illustrate different facets.

**Consolidate; don't map one-to-one.** This repo's 13 files came from 19 source memories. Overlapping
rules should become one file with sections, not many files that cross-reference each other.

**If a machine's existing rule contradicts one here, stop and raise it with Ky.** A genuine
disagreement between two accumulated rule sets is a finding about which one is wrong, not a merge
conflict to resolve by precedence.

**Raise a *possible* conflict too, not only a known one.** A rule promoted from one machine binds the
others, where the practice it constrains may already be different. Onboarding the second machine, a
new access rule ("my reach is what we'd accept losing") was flagged as possibly at odds with how the
first machine works, before anyone knew whether it was; Ky confirmed that was the right call. The
promoting machine can't see the other's practice, so the question is the only way it gets checked.

## Step 4 — scrub, and verify the scrub with a positive control

Grep the result for employer identifiers, ticket keys, internal system names, and real credentials
or hostnames. **A zero-result grep proves nothing until you have proven the pattern can match** —
run the same pattern against the original un-scrubbed sources and confirm it hits there. Building
this repo, that control caught a real leak that had survived a confident manual review: a code
example copied verbatim from an employer codebase.

`check-rules.py` automates only the *shape* half of this (see **Checks** below). **It does not
replace this step** — it cannot know your employer's system names, because a deny-list of them in
this repo would itself be the leak. Reconciliation still needs a human-run, named-pattern scrub with
a real positive control.

## Step 5 — human review before anything goes live

Write everything into the repo working tree. **Do not commit, do not push, and do not create the
symlink** until Ky has read the result. Reconciliation involves judgment calls about what to drop,
and those are reviewable only while they are still proposals.

## Step 6 — commit, then install

```sh
cd ~/dev/personal-tools && git add claude && git commit && git push

# Preserve anything already there as an INPUT to step 3, not as a graveyard:
mv ~/.claude/rules ~/.claude/rules.premerge   # skip if it does not exist

ln -s ~/dev/personal-tools/claude/rules ~/.claude/rules
```

Verify by starting a session and confirming the rules appear as global instructions.

## Step 7 — close the loop

- **Only once its contents are reconciled**, delete `~/.claude/rules.premerge`. While it exists, this
  machine's onboarding is unfinished.
- **Delete superseded originals from project memory.** A collaboration memory that a rule here now
  supersedes should be removed, not left to drift against it.
- **Record one project memory pointing at this repo**, so future sessions on this machine know that
  collaboration-level insights belong here rather than in project memory.

---

## Where a new insight goes

- **About how we collaborate, or Claude's general behaviour** → a rule file here. Commit and push so
  the other machines get it.
- **About a specific project, repo, or dataset** → that project's memory directory, not here.

Without this split the repo becomes a one-time snapshot that rots, because insights learned during
project work land in project memory and never reach the other machine.

## Writing a rule: what is always-on, and what isn't

`rules/editing-these-rules.md` is the always-loaded summary of this section, so that it is in front
of whoever is about to edit a rule; this is the full version.

### Why there is a budget

Claude Code warns at session start when the instruction files it loads at launch exceed **150,000
characters combined**. Launch-time files aren't truncated — the warning is a heuristic for "this much
context may reduce adherence" — but the rules alone reached 136,786 characters on 2026-11-11 and put
any project with a modest `AGENTS.md` over the line. They had grown from 81k to 137k in about two and
a half days, entirely by appending.

`check-rules.py` warns when always-on rules exceed `ALWAYS_ON_BUDGET` (130,000: the 150k limit minus
the largest launch-time project instruction file on the first machine, 20k). The constant's comment
says when to revisit it, including once the second machine's largest is known.

### The test: does this sentence change what I do?

The reader of a rule is Claude, in every session. So the test for keeping a sentence in an always-on
rule is **whether it changes what Claude does in a session where it is loaded** — the same symmetric
test `praise-is-a-spec.md` uses for recaps.

- **Stays in the rule:** the trigger, the reasoning, and **at least one worked example good enough to
  recognise the pattern.** A rule stripped to its conclusion reads as an unreasoned imperative: it is
  either ignored or applied as a blanket, which is the failure `verbosity-and-nuance.md` describes
  from the other side. **Never cut a worked example to save space.**
- **Moves to `rationale/`:** text that only defends or dates the rule — the sample-by-sample evidence
  trail, the history of earlier wrong readings, "why the neighbouring rules don't already cover
  this", where an example came from. That is what you need when *revising* a rule, and revising
  means opening the file, which is exactly where the pointer sits.
- **Stays inline even though it looks like history:** a revisit condition I would need to recognise
  mid-session ("what would reopen it"), and an open agenda that is still awaiting a decision. Moving
  either out of sight is how it gets discovered rather than decided.

### Three habits that keep it from growing back

1. **A unification is a refactor, not a bridge.** When two rules turn out to be one idea, state it
   once in the file that owns it and replace the other statements with a pointer. The capability vs
   mechanism boundary had been stated four times, about 4,300 characters, because each unification
   added a bridge sentence to both files and removed nothing.
2. **A corroboration updates the evidence line.** "Three for three, across two kinds of guard" goes in
   the rule; the narrative of the third sample goes to `rationale/`.
3. **A consolidation carries a ledger.** Every passage removed from an always-on rule gets a line in
   the commit message saying where it went: "now stated once in X", "moved to `rationale/Y`", or
   "deleted because…". A deletion with no destination is visible on the page, which is what a reviewer
   is checking for.

**Why a pointer to a sibling rule loses nothing:** every always-on rule is in context at the same
moment, so "told in full in `test-data-and-coverage.md`" puts the full telling one glance away at the
point of use. That stops being true for a rule moved out of the always-on set; before path-scoping a
rule, or making it a skill, check what points *into* it.

### Path-scoped rules

A rule with `paths:` frontmatter loads only when Claude reads, writes or edits a matching file. The
patterns are relative to the session's primary working directory. Measured 2026-11-11 with canary
words in headless sessions, against the two code-style rules: a `.go` read loaded neither, `.py`
loaded the general rule only, `.ts` loaded both, and no read loaded neither. (Asking the model whether
a rule was present, without a canary, was useless — it said yes to both after the `.go` read.)

**The gap:** the rule arrives *with* the tool result, so the first `Write` of a brand-new file, in a
session that has read no matching file yet, happens without it. Fit for rules about writing code in
an existing codebase; wrong for anything dispositional, whose trigger is not a file type. If
frontmatter fails to parse, Claude Code silently loads the rule everywhere, and the checker would
still count it as path-scoped — so verify a new pattern with a canary rather than trusting the count.

## Layer the specifics in project memory

*The first machine's idea; the second machine built it.* A rule here holds the principle and a
de-identified worked example. **The specific instance — the real system, ticket, file, command —
stays in that project's memory, as a thin layer that cites the rule.** One lesson, two layers:

- **The rule** says what to do and why, in terms that hold anywhere.
- **The project memory** says what that means *here*: "the rule's 'reused dev server' is this repo's
  Playwright config, which reuses `:5173` outside CI." It does not restate the principle — a restated
  principle drifts from the rule — it maps the rule onto this project.

**Why both layers, not just the rule:**

- **The de-identified example has lost the mapping a project session needs.** "An upstream service"
  is the right thing to write here and useless when you're standing in the codebase wondering which
  upstream. The layer gives it back, locally, where it can't leak.
- **Some details are only actionable in one project** and have nowhere else to live. Onboarding the
  second machine, deleting a fully-superseded memory threw one away (the `:5173` detail above) until
  this idea recovered it. **When a rule absorbs a memory, trim the memory to its specific layer;
  delete it only if nothing specific is left.**
- **When a rule changes, its instances can be found and re-checked** — a revised rule may change what
  an instance should say.
- **It orders the scrub.** Write the specific instance first, then generalise a copy into the rule.
  The original is never the thing being edited down.

**How a memory cites a rule: the full path, `~/.claude/rules/<file>.md`.** A bare `<file>.md` in a
memory is ambiguous with the project's own files (`AGENTS.md`, `README.md`). `check-rules.py` reads
this machine's project memories and fails if a cited rule doesn't exist.

**These links are one-way and machine-local.** A rule never cites a memory (that would be the leak),
and each machine's memories are invisible to the other. So **after renaming or deleting a rule, run
`check-rules.py` on each machine** — the other machine's broken citations only show up there.

## Governance: who approves a new rule

**Interim rule (set 2026-11-09): surface every addition in-session and let Ky read the diff before
commit.** One line is enough — "I've added X to the rules because Y." He is not reviewing each rule
on its merits; he is vetting a process that is genuinely novel.

**Ky's stated long-term intent is the opposite: this repo is Claude's to maintain**, written and
committed without asking. The gate above exists only until the process has proven itself.

**The burden of retiring the gate is Claude's, not Ky's.** An interim measure with no review trigger
becomes permanent by inertia, and the person who has to remember it is the one who didn't ask for
it. So: once additions have been landing without needing correction, **propose retiring the gate**
rather than waiting to be told.

**Why the gate is not merely ceremony while it lasts:** a bad rule here is self-reinforcing in a way
a bad project memory is not. It loads unconditionally, in every session, on every machine, and it
shapes how everything else is read — including any later judgement about whether to revise it.

## Checks

```sh
python3 claude/check-rules.py        # exit 0 = pass, 1 = problems
```

Run it after editing rules, and before any commit that touches them. It checks:

- **only `.md` files in `rules/`** — anything there is loaded every session.
- **every rule has an H1** — catches a truncated or corrupt write. Found after any frontmatter, and
  checked in `rationale/` too.
- **rationale pointers** — every `` `rationale/<f>.md` `` a rule cites must exist, and every rationale
  file must be cited by some rule: an unreferenced one is lost, since nothing at session start leads
  to it.
- **always-on budget** — warns when rules without `paths:` exceed `ALWAYS_ON_BUDGET`. The totals are
  printed in characters (the harness's unit), split into always-on, path-scoped and rationale.
- **cross-references resolve** — rules cite each other by filename, so those names *are* links and a
  rename breaks them silently. This is the check the tool was written for.
- **leak patterns live** — each leak shape must still match a synthetic sample. A scan that finds
  nothing proves nothing unless its patterns are proven able to match; a silently-broken regex is
  precisely the vacuous read `rules/evidence-and-claims.md` warns about.
- **leak-shape scan** — over `rules/` and `rationale/` alike — ticket-key, email, internal-hostname,
  private-IP, account-id and credential *shapes*. Deliberately shape-based, never name-based, for the reason in step 4. **Treat it as a
  tripwire, not as proof.**
- **memory -> rule refs** — every `~/.claude/rules/<file>.md` cited from this machine's project
  memories (under `$CLAUDE_CONFIG_DIR`, default `~/.claude`) must exist. Prints how many memories cite
  rules, so a zero is visible. Machine-local by nature; see **Layer the specifics in project memory**.
  Mutation-checked: a fixture memory citing a nonexistent rule makes it fail.
- **orphan report** — warns when a rule is cited by no other. Informational: a leaf rule is fine; this
  just makes it a deliberate choice rather than an accident.

It also prints the total size, since every byte is context spent in every session on every machine.

Verified end to end: planting a fake ticket key and email in a throwaway rule makes it fail, and
removing them makes it pass again.

## Git is the only cross-machine channel — don't re-try peer messaging

**Settled 2026-11-09, after spending a session restart on it.** Claude Code's `ListAgents` /
`SendMessage` peer discovery runs over **per-session Unix domain sockets** in `/tmp/cc-socks/`, one
per session. A UDS is filesystem-local by construction, so **sessions on different machines can never
see each other through it**, with or without Remote Control. `--remote-control <name>` is an address
label, not a room: two sessions given the same name become two same-named peers needing a `[ref]` to
disambiguate, not participants in a shared channel.

So the coordination channel between machines is **this repo**, plus Ky relaying. That is not a
consolation prize — the onboarding reconciliation below is written for exactly this, and it works:
the second machine's one substantive finding of that day (that the shell helper *does* load there)
arrived via Ky and immediately rewrote `rules/shell-environment.md`.

**The tools' own descriptions say otherwise, which is why the revisit condition matters.** On the
second machine, `ListAgents` describes listing "Remote Control sessions on other machines" when
Remote Control is connected, and `SendMessage` describes delivering to a session "on another machine".
With `/remote-control` run in both sessions, neither appeared: `ListAgents` reported only local
sessions, twice, and a send by the Remote Control name returned "not reachable", twice. So a remote
path exists on paper and did not exist for us; the conclusion is about what we could reach, and the
mechanism above is why the local path can't be it.

**Revisit if** `ListAgents` ever lists a session whose reply address is not a `uds:` path — that would
mean a non-local transport exists and this conclusion is stale. Until then, don't spend turns on it.

## Sync discipline

`~/.claude/rules` is a symlink into this working tree, so edits made during a session show up as
uncommitted changes here. **Changes go through a pull request**, like the rest of our work
(`rules/git-discipline.md`) — Ky's call on 2026-11-11, to apply our discipline to our own tooling
too, after the repo had been taking direct commits to `main`. Pull on the other machine before
starting work.

**What a pull request here does and doesn't gate:** because of the symlink, whatever branch is
checked out on a machine is already live on that machine — review gates what reaches `main` and the
other machine, not what the authoring machine is running. Switch back to `main` after opening the
pull request if the change shouldn't be in effect locally until it merges. One file per rule keeps merge conflicts rare and file-scoped — there is intentionally
no index file, since every rule is loaded regardless.
