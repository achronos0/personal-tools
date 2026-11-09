# Claude Code configuration

Portable, machine-independent configuration for working with Claude Code. Cloned and symlinked on
each machine so the same collaboration norms apply everywhere, and so a rule learned on one machine
reaches the others through git.

## Layout

- `rules/` — global instruction files. Claude Code loads every `*.md` in `~/.claude/rules/`
  automatically, in every session, in every project. No configuration needed: the directory's
  presence is the wiring.

This README lives *outside* `rules/` on purpose — anything inside that directory is loaded into
context on every single session, so it holds only content meant for Claude to act on.

## What belongs here, and what doesn't

**Belongs here:** how Ky and Claude work together, how Claude should respond, how to think about
work, general engineering values, language-level style preferences, machine/shell environment facts.

**Does not belong here:** anything specific to a project or repository — that goes in project memory
or the repo's own `AGENTS.md` / `CLAUDE.md`. And **nothing employer-related whatsoever**: no code,
system names, ticket keys, data, metrics, or internal process. Worked examples in these files are
deliberately de-identified; keep it that way when editing.

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
- **every rule has an H1** — catches a truncated or corrupt write.
- **cross-references resolve** — rules cite each other by filename, so those names *are* links and a
  rename breaks them silently. This is the check the tool was written for.
- **leak patterns live** — each leak shape must still match a synthetic sample. A scan that finds
  nothing proves nothing unless its patterns are proven able to match; a silently-broken regex is
  precisely the vacuous read `rules/evidence-and-claims.md` warns about.
- **leak-shape scan** — ticket-key, email, internal-hostname, private-IP, account-id and credential
  *shapes*. Deliberately shape-based, never name-based, for the reason in step 4. **Treat it as a
  tripwire, not as proof.**
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

**Revisit if** `ListAgents` ever lists a session whose reply address is not a `uds:` path — that would
mean a non-local transport exists and this conclusion is stale. Until then, don't spend turns on it.

## Sync discipline

`~/.claude/rules` is a symlink into this working tree, so edits made during a session show up as
uncommitted changes here. Commit and push them deliberately; pull on the other machine before
starting work. One file per rule keeps merge conflicts rare and file-scoped — there is intentionally
no index file, since every rule is loaded regardless.
