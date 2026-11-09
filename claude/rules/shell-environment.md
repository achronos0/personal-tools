# Ky's shell environment

His zsh sources `personal-tools/bin/macos_shell_helper.sh`, which defines aliases and helper
functions. **Whether they are live in my Bash tool is machine-dependent** — confirmed the hard way:
absent on one of his machines, present and biting on another.

## The discriminator: a TTY guard in `.zshrc`

On the machine where they are absent, `~/.zshrc` line 1 is:

```sh
[[ -t 0 ]] && source ~/bin/macos_shell_helper.sh
```

`[[ -t 0 ]]` is true only when **stdin is a TTY**, and Claude Code's shells have no TTY on stdin, so the
guard fails and the helper is never sourced. Verified both directions there: `zsh -c`, `zsh -ic` and
`zsh -lic` all lack `gc` / `ll` / `alias cp`, while sourcing the file by hand in the same shell defines
all of it correctly. The helper is fine; it simply isn't loaded.

**On a machine without that guard, everything below is live.** Measured on the second machine
(Claude Code 2.1.319, zsh 5.9), whose `~/.zshrc` sources the helper unguarded: `type` reports `cd`,
`gc`, `gca`, `gcr`, `gp`, `gx`, `gi` and `trash` as functions from the shell snapshot, and `cp` / `mv`
as the `-iv` aliases.

**So check, don't assume — one line, at the start of work on an unfamiliar machine:**

```sh
grep -n 'macos_shell_helper' ~/.zshrc   # guarded by [[ -t 0 ]]?  -> helpers absent
type cp gc 2>&1 | head -2               # or just ask the shell directly
```

**Where the helper IS loaded, these are the consequences that matter:**

- **`cp` and `mv` are `cp -iv` / `mv -iv`** and will **block on an interactive prompt** when
  overwriting — this is the original observed hang, and it is real, not historical: on the second
  machine a test check hung for five minutes on an overwrite prompt before Ky interrupted it, and left
  a file half-edited. **Use `/bin/cp`, `/bin/mv`, `/bin/rm` for any overwrite.** Not insurance:
  load-bearing.
- **The one-letter git helpers below exist and are callable**, several of which push or delete without
  further confirmation. Never invoke them by reflex.
- **`cd` is wrapped** to print a directory listing and, where `.git` is a directory, `gi nofetch` (the
  last commit and `git status`). **The output is the hazard:** anything captured with
  `$(cd dir && cmd)` carries the listing with it. On the second machine that put directory listings
  into two PR descriptions, built from `$(cd repo && gh pr create …)`. Never `cd` inside a command
  substitution — use `git -C <dir>`, `gh -R <owner/repo>`, a tool's own path flag, or
  `cd dir >/dev/null`. Check any captured text for listing lines before posting it.

**Do not mistake the `grep` function for one of his.** `type grep` resolves to a function in Claude
Code's shell snapshot, which looks like a survivor but is **the harness's own wrapper** — it dispatches
to `$CLAUDE_CODE_EXECPATH` with `ARGV0=ugrep`. His `grep` alias is separately gated on
`/usr/local/bin/ggrep`. The snapshot strips nothing: it carries 132 functions, all nvm and
zsh-completion machinery configured without a TTY guard.

**And the wrapper has its own hazard:** it runs ugrep with `--ignore-files`, which honours
`.gitignore`, so a recursive search from a repo root silently skips gitignored directories — measured
as 0 hits against `command grep`'s 4. Details and the control in `evidence-and-claims.md`.

## The Bash tool runs zsh, not bash

Despite the tool's name, the shell is Ky's login shell. Three zsh behaviours have broken commands
written as if for bash:

- **Unquoted variables are not word-split.** `set -- $r` or `for x in $list` with a space-joined
  string passes the whole string as one argument. Use an array, or a function called with separate
  arguments.
- **An unmatched glob is an error** (`no matches found`), not a literal. Quote globs that may match
  nothing, or check first.
- **`[` and `]` in a URL are glob characters** — pass `curl -g`, or quote the URL.

## What his git shortcuts actually do

This is the part that matters: several of his one- to four-letter helpers are **write operations
that reach the remote**. When he says "I ran `gca`", he has already pushed.

| He says | It runs |
| --- | --- |
| `gc '<msg>'` | `git pull && git commit -m '<msg>' && git push` |
| `gca '<msg>'` | `git pull && git add --all && git commit && git push` |
| `gcr` / `gcra` | `git commit --amend --no-edit && git push --force-with-lease --force-if-includes` (`gcra` adds `--all` first) |
| `gp` | `git pull && git push && git fetch --all --prune` |
| `gpf` | `git push --force-with-lease --force-if-includes` |
| `gg <branch>` | switch to branch, **creating local + remote** if absent |
| `ggp <branch>` | switch, pull, push, fetch |
| `gx [branch]` | **delete branch local AND remote** (refuses `main`) |
| `gi` | `git fetch` + `git show` summary + `git status --short` |
| `gs` / `gd` / `gl` | status (all untracked) / `diff -w` / log |
| `ga [files]` | `git add` those files, or `--all` if none given |
| `ghpr <base>` | `gh pr create --fill --base=<base>` |
| `lg` / `mg` | run `gi` / an arbitrary command across every git repo found recursively |

Two consequences:

- **"I committed it" from him usually means it is already pushed.** `gc` and `gca` push, and both
  `pull` first. Don't offer to push afterwards, and don't assume the remote is behind.
- **His amend shortcuts force-push by default**, with `--force-with-lease --force-if-includes`. If a
  branch is under review, the merge-vs-rebase reasoning in `git-discipline.md` applies to his
  shortcut too — worth saying so before he reaches for `gcr`.

## Other environment facts

- **`cd` is wrapped** to list the directory and, inside a repo, print `gi nofetch` output — no
  fetch. It is why his terminal shows git state after every `cd`, and on a machine where the helper
  loads it applies to my shells too (see the capture hazard above).
- **`cp`/`mv` prompt on overwrite** wherever the helper loads — covered above; `/bin/cp`, `/bin/mv`,
  `/bin/rm` for overwrites, and treat it as a live hazard rather than insurance.
- **`EDITOR=nano`**, but Claude Code sets `GIT_EDITOR=true`, so an editor-opening git command is a
  no-op here rather than a hang. Still pass `-m` / `--no-edit` explicitly.
- **GNU coreutils is installed on one machine and not the other — and it is not what the `grep`
  switch keys on.** Where coreutils is installed (Homebrew, `/opt/homebrew`), the helper's `ll` uses
  `gls`, found via `whence`, so that part follows coreutils. But the `grep` → `ggrep --perl-regexp`
  and **case-insensitive `fgrep`** aliases are gated on `-x /usr/local/bin/ggrep`. `ggrep` comes from
  Homebrew's separate `grep` package, not coreutils (the helper's comment conflates them), and
  `/usr/local` is the Intel Homebrew prefix. On Apple Silicon that test can never pass, even with GNU
  grep installed. The trigger worth re-checking for is "`/usr/local/bin/ggrep` exists", not
  "coreutils got installed".
- `trash <path>` moves to `~/.Trash` rather than deleting; `rmds` deletes `.DS_Store` recursively.

## What is settled, and what this file got wrong twice

**Durable:** the git-shortcut table — read from `bin/macos_shell_helper.sh` in this repo, so exactly as
current as that script, and relevant on any machine where the helper loads.

**Durable:** the TTY guard as the *discriminator*. It explains both machines rather than one.

**Measured on both machines:** `GIT_EDITOR=true` in Claude Code's shell. Still not explained by a
mechanism we have read, so re-check after a major harness upgrade.

**Machine-dependent, not provisional:** whether GNU coreutils is installed. The rule that matters is
the `ggrep` gate above, which reads a fixed path.

**Two superseded claims, kept because the sequence is the lesson:**

1. *"Claude Code's shell snapshot strips his aliases."* Wrong about the cause. Generalised from probe
   results on one machine; the snapshot strips nothing.
2. *"This file is waiting on another machine's lived reality."* Right that one machine couldn't settle
   it, wrong that a probe was needed — the archaeology question in `engineering-values.md` found the
   cause from inside one machine, which is cheaper than waiting.

Then the second machine contradicted the behaviour anyway, and the rule's own instruction applied: **on
a contradiction, rewrite rather than patch** — because two machines disagreeing meant the universal was
wrong, not that one was an exception. What survived the rewrite is the mechanism, now doing the work it
is actually good for: telling the two machines apart.

**A third, small one, from the rewrite itself:** it said `cd` runs a `git fetch`. It doesn't — the
wrapper calls `gi nofetch`. The claim came from applying the table's row for bare `gi` to the wrapper
without reading the wrapper's call: `evidence-and-claims.md`'s "trace the value, not the expression",
in miniature.
