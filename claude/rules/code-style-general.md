# Code style preferences — all languages

Cross-language preferences of Ky's. Language-specific nitpicks live in `code-style-<language>.md`
instead; where no such file exists, follow the conventions of the code at hand.

## Control statements always use braced blocks

In any language that *permits* a braceless body, always use a block. Opening brace on the same line;
body on the next line.

```c
// ✓ indented, and the indentation is real
if (condition) {
    doSomething();
}

// ✗ bad — nothing is indented, so the branch is invisible at a scan
if (condition) doSomething();

// ✗✗ worst — indented but NOT a block; it reads exactly like the correct form
if (condition)
    doSomething();
```

**Never emit a braceless control statement, even for a single-line body**, and never rely on a
linter to catch it — many don't.

**Where this bites:** C, C++, C#, Java, JavaScript, TypeScript, PHP, Swift — anywhere the grammar
allows a bare statement as the body of `if` / `else` / `for` / `while`.

**Where there is nothing to get wrong:** Go and Rust require a block already, and Go additionally
mandates the opening brace on the same line (moving it breaks semicolon insertion), so `gofmt`
output is correct by construction.

**Python analogue:** the braced form doesn't exist, but the single-line `if cond: do_something()`
is the same shape and the same preference applies — put the body on its own line.

**Why — Ky's reason, which is visual first:** he wants to *see* the branch body **indented**, so
that at a scan it is obvious there **is** a branch. Indentation is the signal; the braces are what
make the signal true.

**That ranks the two wrong forms unequally.** The single-line form is bad because nothing is
indented, so the branch is invisible. **The newline-without-braces form is worse**, because it is
indented *and is not a block* — it reads exactly like the correct form, so the visual cue lies.
Adding a second statement then silently places it outside the conditional while the diff looks
innocent. A braceless body is a correctness hazard, and the newline variant is the greater one
precisely because it looks safe.
