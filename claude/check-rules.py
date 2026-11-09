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


def read(f):
    with open(os.path.join(RULES, f), encoding="utf-8") as fh:
        return fh.read()


def check_only_markdown():
    stray = [f for f in sorted(os.listdir(RULES)) if not f.endswith(".md")]
    for f in stray:
        failures.append("rules/%s is not a .md file; everything in rules/ is loaded every session" % f)
    return not stray


def check_has_h1():
    ok = True
    for f in rule_files():
        lines = [ln for ln in read(f).splitlines() if ln.strip()]
        if not lines or not lines[0].startswith("# "):
            failures.append("rules/%s has no top-level '# ' heading (truncated or corrupt write?)" % f)
            ok = False
    return ok


def check_links_resolve():
    present, ok = set(rule_files()), True
    for f in rule_files():
        for ref in sorted(set(MD_REF.findall(read(f)))):
            if ref not in present:
                failures.append("rules/%s references `%s`, which does not exist" % (f, ref))
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
    for f in rule_files():
        for lineno, line in enumerate(read(f).splitlines(), 1):
            for label, pat in LEAK_SHAPES:
                for m in pat.finditer(line):
                    if label == "ticket key" and SHAPE_ALLOW.match(m.group(0)):
                        continue
                    failures.append("rules/%s:%d possible %s: %r" % (f, lineno, label, m.group(0)))
                    ok = False
    return ok


def main():
    checks = [
        ("only .md files in rules/", check_only_markdown),
        ("every rule has an H1",    check_has_h1),
        ("cross-references resolve", check_links_resolve),
        ("leak patterns live",       check_shape_patterns_live),
        ("leak-shape scan",          check_leak_shapes),
        ("orphan report",            check_orphans),
        ("memory -> rule refs",      check_memory_refs),
    ]
    print("checking %s\n" % RULES)
    for name, fn in checks:
        print("  %-28s %s" % (name, "ok" if fn() else "FAIL"))

    total = sum(len(read(f)) for f in rule_files())
    print("\n  %d rule files, %d bytes (~%d tokens loaded every session)"
          % (len(rule_files()), total, total // 4))

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
