# Rationale: Ky's shell environment

*Not loaded at session start. This file records how `shell-environment.md` reached its current shape.
The two facts from here that matter day to day — the shortcut table is only as current as the helper
script, and `GIT_EDITOR=true` should be re-checked after a harness upgrade — now sit in the rule next
to what they qualify. Read this before revising the rule.*

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
