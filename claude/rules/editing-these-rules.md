# Editing these rules

**Before adding to or changing any file in `~/.claude/rules/`, read `claude/README.md` in
personal-tools ("Writing a rule"), and run `claude/check-rules.py` after.** Every rule loads in every
session on every machine, against a combined size limit the harness warns about, and these files grew
by appending until they crossed it. The three habits that stop that:

- **A unification is a refactor, not a bridge.** When two rules turn out to be one idea, state it once
  where it belongs and replace the other statements with a pointer. Adding "this is X applied to Y"
  to both files while keeping both statements is how one idea came to be stated four times.
- **A new corroboration updates the evidence line; its narrative goes to `claude/rationale/`.**
  Keep in the rule what changes what I do: the trigger, the reasoning, and one worked example good
  enough to recognise the pattern. Move what only defends or dates the rule.
- **Never cut a worked example to save space.** A rule without its example reads as an unreasoned
  imperative, and either gets ignored or applied as a blanket. Cut restatement, not reasoning.
