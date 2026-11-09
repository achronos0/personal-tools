# Ky's shell environment

His zsh sources `personal-tools/bin/macos_shell_helper.sh`, which defines aliases and helper
functions. **Since v2.4.0 of the helper (2026-11-09), its interactive conveniences stay out of my Bash
tool on every machine:** when stdin is not a TTY — and Claude Code's shells never have one — the
helper forces `prompt`, `list_on_cd`, `friendly_commands`, `helper_commands` and `nvm_autoload` off.
PATH additions, colour, `EDITOR` and shell settings still apply.

So in my shell: no `gc`/`gx`/`gi`/`ll`, `cd` is the builtin, `cp`/`mv` are not aliased, and no `grep`
alias. **Check, don't assume — one line at the start of work on an unfamiliar machine, or after a
helper change:**

```sh
type cp gc cd 2>&1 | head -3   # expect: cp is /bin/cp, gc not found, cd is a shell builtin
```

**A session snapshots its shell at start.** One started before a helper change keeps the old
behaviour until it is restarted.

## If the guard is ever bypassed

An older copy of the helper, a shell that does have a TTY, or a guard removed by mistake brings all of
this back. These are the hazards it exists to remove — all observed, none hypothetical:

- **`cp` and `mv` are `cp -iv` / `mv -iv`** and **block on an interactive prompt** when overwriting.
  A test check once hung five minutes on one and left a file half-edited. Using `/bin/cp`, `/bin/mv`
  and `/bin/rm` for overwrites costs nothing, so keep doing it regardless.
- **The one-letter git helpers below exist and are callable**, several of which push or delete without
  further confirmation.
- **`cd` prints a directory listing** and, where `.git` is a directory, `gi nofetch` (last commit and
  `git status` — no fetch). Anything captured with `$(cd dir && cmd)` carries that listing with it;
  it once put directory listings into two PR descriptions, built from `$(cd repo && gh pr create …)`.
  **Never `cd` inside a command substitution** — use `git -C <dir>`, `gh -R <owner/repo>`, or a tool's
  own path flag. That's good practice even with the guard in place.

## Claude Code's own `grep`

`type grep` resolves to a function in Claude Code's shell snapshot. It is **the harness's own
wrapper**, not Ky's — it dispatches to `$CLAUDE_CODE_EXECPATH` with `ARGV0=ugrep` — so it is no
evidence about whether his helper loaded.

**It has a hazard of its own:** it runs ugrep with `--ignore-files`, which honours `.gitignore`, so a
recursive search from a repo root silently skips gitignored directories — measured as 0 hits against
`command grep`'s 4. Details and the control in `evidence-and-claims.md`.

## The Bash tool runs zsh, not bash

Despite the tool's name, the shell is Ky's login shell. These zsh behaviours have broken commands
written as if for bash:

- **Unquoted variables are not word-split.** `set -- $r` or `for x in $list` with a space-joined
  string passes the whole string as one argument. Use an array, or a function called with separate
  arguments.
- **An unmatched glob is an error** (`no matches found`), not a literal. Quote globs that may match
  nothing, or check first.
- **`[` and `]` in a URL are glob characters** — pass `curl -g`, or quote the URL.
- **`path` is tied to `PATH`.** A function with `local path=…`
  replaces the command search path for its body, and everything in it fails with "command not found".

## What his git shortcuts actually do

These run in **his** terminal, not mine — the table is for reading what he tells me. Several of his
one- to four-letter helpers are **write operations that reach the remote**. When he says "I ran
`gca`", he has already pushed.

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

- **`EDITOR=nano`**, but Claude Code sets `GIT_EDITOR=true`, so an editor-opening git command is a
  no-op here rather than a hang. Still pass `-m` / `--no-edit` explicitly.
- **His interactive `grep` becomes GNU grep wherever `ggrep` is on PATH** (Homebrew's `grep`
  package — not coreutils): `grep` gets `--perl-regexp`, and `fgrep` (and his `f` alias) becomes
  **case-insensitive**. Before v2.4.0 the gate was a fixed `/usr/local/bin/ggrep`, the Intel Homebrew
  prefix, so on Apple Silicon it never fired. GNU grep rejects `-P` with `-E` ("conflicting matchers
  specified"), so with the alias active a typed `grep -E` errors. None of this reaches my shell
  (`friendly_commands` is off there).
- `ll` uses GNU `gls` where coreutils is installed (one machine has it, one doesn't).
- `trash <path>` moves to `~/.Trash` rather than deleting; `rmds` deletes `.DS_Store` recursively.

## How this file got here

**Durable:** the git-shortcut table — read from `bin/macos_shell_helper.sh` in this repo, so exactly as
current as that script. And the helper's own non-TTY guard, which travels with the repo, so it holds on
any machine that sources it — `.zshrc` differences no longer matter.

**Measured on both machines:** `GIT_EDITOR=true` in Claude Code's shell. Not explained by a mechanism
we have read, so re-check after a major harness upgrade.

**The sequence, kept because it is the lesson:**

1. *"Claude Code's shell snapshot strips his aliases."* Wrong about the cause; generalised from one
   machine. The snapshot strips nothing.
2. *"This file is waiting on another machine's lived reality."* The archaeology question in
   `engineering-values.md` then found the cause from inside one machine: a `[[ -t 0 ]] &&` guard on
   that machine's `.zshrc` line. Cheaper than waiting.
3. The second machine had no such guard, and everything bit there — a contradiction, so the file was
   **rewritten rather than patched**, around the guard as the discriminator between machines.
4. That rewrite said `cd` runs a `git fetch`. It doesn't — the wrapper calls `gi nofetch`; the claim
   applied the table's row for bare `gi` without reading the wrapper's call (`evidence-and-claims.md`,
   "trace the value, not the expression").
5. **Then the fix moved to the source.** A per-machine `.zshrc` guard was the right diagnosis and the
   wrong place for the remedy: it has to be remembered on every machine. The helper now guards itself,
   and the discriminator became a one-line check. Same root-cause move as `engineering-values.md`:
   once you know why two machines differ, remove the reason rather than document it.
