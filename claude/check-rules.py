#!/usr/bin/env python3
"""Integrity checks for claude/rules/.

Run:  python3 claude/check-rules.py        (exit 0 = pass, 1 = fail)

Why Python and not shell: macOS ships BSD grep and CI runs GNU grep; the two
disagree about \\b and friends. One regex dialect is worth the import.

NOTE ON THE LEAK SCAN: it matches *shapes* (a ticket-key shape, an email shape,
a key shape), never specific employer names. A deny-list of real system names
would itself be the leak it exists to prevent. That makes this scan weaker than
a named one: it is a tripwire, not proof. The real positive-control scrub -- run
the pattern against the un-scrubbed sources to prove it can match -- needs those
sources, so it stays a manual step in the onboarding procedure (README step 4).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(ROOT, "rules")
# Text that defends or dates a rule -- its evidence trail, how it was found, why
# it is needed -- lives here, NOT in rules/, so it never loads at session start.
# A rule points at its rationale file; the pointer is the only way to find it.
RATIONALE = os.path.join(ROOT, "rationale")

# Claude Code warns when the files loaded at session start exceed 150,000 chars
# combined. Rules without `paths:` frontmatter load in every session, alongside
# the project's own CLAUDE.md/AGENTS.md. 130,000 = 150,000 minus 20,000, the
# largest launch-time project instruction file on the first machine (2026-11-11).
# Revisit if the harness limit changes, or if a project either machine starts
# sessions in has a bigger one -- the second machine's figure is not known yet.
ALWAYS_ON_BUDGET = 130_000

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
RATIONALE_REF = re.compile(r"`rationale/([a-z0-9][a-z0-9-]*\.md)`")

# Tokens matching a leak shape that are standard technical vocabulary, or are
# obvious placeholders. A real ticket is never numbered 0000, so an all-zero
# suffix is a placeholder by construction -- which keeps the rules free to cite
# a fake key as an example of what not to fabricate.
SHAPE_ALLOW = re.compile(
    r"^(?:(?:UTF|ISO|RFC|SHA|AES|RGB|WCAG|HTTP|IPV|ES)-?[0-9]+|[A-Z]{2,6}-0+)$", re.I)

LEAK_SHAPES = [
    ("ticket key",        re.compile(r"\b[A-Z]{2,6}-[0-9]{3,6}\b")),
    ("email address",     re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("internal hostname", re.compile(r"\b[a-z0-9][a-z0-9-]*\.(internal|corp|intranet|lan)\b", re.I)),
    ("private IP",        re.compile(r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)[0-9]{1,3}\.[0-9]{1,3}\b")),
    ("12-digit account",  re.compile(r"(?<![0-9,.])[0-9]{12}(?![0-9,.])")),
    ("AWS access key",    re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token",      re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("Slack token",       re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("slack webhook",     re.compile(r"hooks\.slack\.com/\S+")),
]

MD_REF = re.compile(r"`([a-z0-9][a-z0-9-]*\.md)`")

# Project memory layers specific instances on top of these rules and cites them by
# full path (README: "Layer the specifics in project memory"). The full path is
# the convention because a bare `foo.md` in a memory is ambiguous with the
# project's own files (AGENTS.md, README.md, ...).
MEMORY_RULE_REF = re.compile(r"~/\.claude/rules/([a-z0-9][a-z0-9-]*\.md)")
MEMORY_REF_SAMPLE = ("see `~/.claude/rules/git-discipline.md` here", "git-discipline.md")

# Positive control: every shape must still match a synthetic sample. A zero
# result from the scan means nothing unless the patterns are proven live, and a
# silently-broken regex is exactly the vacuous read these rules warn about.
# Samples are fabricated and live here, never in rules/.
SELF_TEST = {
    "ticket key":        "ABCD-1234",
    "email address":     "someone@example.com",
    "internal hostname": "db01.internal",
    "private IP":        "10.0.0.1",
    "12-digit account":  "123456789012",
    "AWS access key":    "AKIAABCDEFGHIJKLMNOP",
    "GitHub token":      "ghp_abcdefghijklmnopqrstuvwxyz0123",
    "Slack token":       "xoxb-abcdefghijkl",
    "private key block": "-----BEGIN RSA PRIVATE KEY-----",
    "slack webhook":     "hooks.slack.com/services/T0/B0/abc",
}

failures, warnings, notes = [], [], []


def rule_files():
    return sorted(f for f in os.listdir(RULES) if f.endswith(".md"))


def rationale_files():
    if not os.path.isdir(RATIONALE):
        return []
    return sorted(f for f in os.listdir(RATIONALE) if f.endswith(".md"))


def read(f, base=RULES):
    with open(os.path.join(base, f), encoding="utf-8") as fh:
        return fh.read()


def all_docs():
    """(label, text) for every file the org-agnostic standard applies to."""
    return ([("rules/" + f, read(f)) for f in rule_files()]
            + [("rationale/" + f, read(f, RATIONALE)) for f in rationale_files()])


def split_frontmatter(text):
    m = FRONTMATTER.match(text)
    return (m.group(1), text[m.end():]) if m else ("", text)


def is_path_scoped(f):
    """A rule with `paths:` loads only when a matching file is read, not at launch."""
    return re.search(r"(?m)^paths\s*:", split_frontmatter(read(f))[0]) is not None


def check_only_markdown():
    stray = [f for f in sorted(os.listdir(RULES)) if not f.endswith(".md")]
    for f in stray:
        failures.append("rules/%s is not a .md file; everything in rules/ is loaded every session" % f)
    return not stray


def check_has_h1():
    ok = True
    for label, text in all_docs():
        lines = [ln for ln in split_frontmatter(text)[1].splitlines() if ln.strip()]
        if not lines or not lines[0].startswith("# "):
            failures.append("%s has no top-level '# ' heading (truncated or corrupt write?)" % label)
            ok = False
    return ok


def check_links_resolve():
    present, ok = set(rule_files()), True
    for label, text in all_docs():
        for ref in sorted(set(MD_REF.findall(text))):
            if ref not in present:
                failures.append("%s references `%s`, which does not exist" % (label, ref))
                ok = False
    return ok


def check_rationale_links():
    """Rules point at rationale files, and every rationale file must be pointed at.
    An unreferenced rationale file is lost: nothing at session start leads to it."""
    present, ok, cited = set(rationale_files()), True, set()
    for f in rule_files():
        for ref in sorted(set(RATIONALE_REF.findall(read(f)))):
            cited.add(ref)
            if ref not in present:
                failures.append("rules/%s points at `rationale/%s`, which does not exist" % (f, ref))
                ok = False
    for f in sorted(present - cited):
        failures.append("rationale/%s is pointed at by no rule, so nothing will lead to it" % f)
        ok = False
    return ok


def check_orphans():
    present = rule_files()
    for f in present:
        if not any(("`%s`" % f) in read(o) for o in present if o != f):
            warnings.append("rules/%s is referenced by no other rule (fine for a leaf)" % f)
    return True


def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")


def memory_files():
    base = config_dir()
    projects = os.path.join(base, "projects")
    if not os.path.isdir(projects):
        return []
    out = []
    for proj in sorted(os.listdir(projects)):
        mem = os.path.join(projects, proj, "memory")
        if os.path.isdir(mem):
            out += [os.path.join(mem, f) for f in sorted(os.listdir(mem)) if f.endswith(".md")]
    return out


def check_memory_refs():
    """Project memories citing a rule must cite one that exists. Machine-local:
    each machine checks its own memories, so run this after any rule rename."""
    found = MEMORY_RULE_REF.findall(MEMORY_REF_SAMPLE[0])
    if found != [MEMORY_REF_SAMPLE[1]]:
        failures.append("memory-ref pattern no longer matches its own sample")
        return False
    present, ok, refs, citing = set(rule_files()), True, 0, 0
    for path in memory_files():
        with open(path, encoding="utf-8") as fh:
            names = MEMORY_RULE_REF.findall(fh.read())
        refs += len(names)
        citing += bool(names)
        for ref in sorted(set(names)):
            if ref not in present:
                failures.append("project memory %s cites ~/.claude/rules/%s, which does not exist"
                                % (os.path.relpath(path, config_dir()), ref))
                ok = False
    notes.append("%d project memories on this machine cite rules (%d references)" % (citing, refs))
    return ok


def check_shape_patterns_live():
    """Prove each leak pattern can still match before trusting that it found nothing."""
    ok = True
    for label, pat in LEAK_SHAPES:
        sample = SELF_TEST.get(label)
        if sample is None:
            failures.append("leak shape %r has no positive-control sample" % label)
            ok = False
        elif not pat.search(sample):
            failures.append("leak shape %r no longer matches its own sample %r" % (label, sample))
            ok = False
    for label in SELF_TEST:
        if label not in dict(LEAK_SHAPES):
            failures.append("positive-control sample %r matches no leak shape" % label)
            ok = False
    return ok


def check_leak_shapes():
    ok = True
    for doc, text in all_docs():
        for lineno, line in enumerate(text.splitlines(), 1):
            for label, pat in LEAK_SHAPES:
                for m in pat.finditer(line):
                    if label == "ticket key" and SHAPE_ALLOW.match(m.group(0)):
                        continue
                    failures.append("%s:%d possible %s: %r" % (doc, lineno, label, m.group(0)))
                    ok = False
    return ok


def check_budget():
    always = sum(len(read(f)) for f in rule_files() if not is_path_scoped(f))
    if always > ALWAYS_ON_BUDGET:
        warnings.append("always-on rules are %d chars, over the %d budget (see ALWAYS_ON_BUDGET "
                        "for where it comes from); consolidate, or move defence to rationale/"
                        % (always, ALWAYS_ON_BUDGET))
    return True


def main():
    checks = [
        ("only .md files in rules/", check_only_markdown),
        ("every rule has an H1",    check_has_h1),
        ("cross-references resolve", check_links_resolve),
        ("rationale pointers",       check_rationale_links),
        ("leak patterns live",       check_shape_patterns_live),
        ("leak-shape scan",          check_leak_shapes),
        ("orphan report",            check_orphans),
        ("memory -> rule refs",      check_memory_refs),
        ("always-on budget",         check_budget),
    ]
    print("checking %s\n" % RULES)
    for name, fn in checks:
        print("  %-28s %s" % (name, "ok" if fn() else "FAIL"))

    # Characters, not bytes: the harness's limit is in characters, and the rules'
    # em-dashes and curly quotes make bytes overstate it by about half a percent.
    always = [f for f in rule_files() if not is_path_scoped(f)]
    scoped = [f for f in rule_files() if is_path_scoped(f)]
    a_chars = sum(len(read(f)) for f in always)
    print("\n  %d always-on rules, %d chars (budget %d, ~%d tokens every session)"
          % (len(always), a_chars, ALWAYS_ON_BUDGET, a_chars // 4))
    print("  %d path-scoped rules, %d chars (load only on a matching read)"
          % (len(scoped), sum(len(read(f)) for f in scoped)))
    print("  %d rationale files, %d chars (never loaded at start)"
          % (len(rationale_files()), sum(len(read(f, RATIONALE)) for f in rationale_files())))

    for n in notes:
        print("  %s" % n)
    for w in warnings:
        print("\nwarn: %s" % w)
    for e in failures:
        print("\nFAIL: %s" % e)
    if failures:
        print("\n%d problem(s)." % len(failures))
        return 1
    print("\nall checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
