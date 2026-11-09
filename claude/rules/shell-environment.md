# Ky's shell environment

His zsh sources `personal-tools/bin/macos_shell_helper.sh`, which defines aliases and helper
functions. **Claude Code's shell snapshot strips those**, so they are generally *not* live in my
Bash tool — verified by probing `type` for each of them in a session where `grep` did resolve to a
function, so the probe was working. Don't assume his conveniences are available to me, and don't
assume his overrides will bite me.

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

- **`cd` is wrapped in his interactive shell** to list the directory and, inside a repo, print `gi`
  output. Not live in mine, but it's why his terminal shows git state after every `cd`.
- **`cp`/`mv` are `cp -iv`/`mv -iv` interactively**, which prompt on overwrite. Once observed to hang
  a tool call; not reproducible now. Using `/bin/cp` and `/bin/mv` for overwrites costs nothing, so
  keep doing it as cheap insurance rather than as a known hazard.
- **`EDITOR=nano`**, but Claude Code sets `GIT_EDITOR=true`, so an editor-opening git command is a
  no-op here rather than a hang. Still pass `-m` / `--no-edit` explicitly.
- **GNU coreutils is not installed.** If it ever is, his interactive `grep` becomes `ggrep
  --perl-regexp` and his `fgrep` becomes **case-insensitive** — both silent behaviour changes worth
  re-checking then.
- `trash <path>` moves to `~/.Trash` rather than deleting; `rmds` deletes `.DS_Store` recursively.

**Maintenance note:** everything here is a measured property of a specific harness version, not of
his dotfiles. If a shell-level surprise shows up, re-probe with `type` before trusting this file.
