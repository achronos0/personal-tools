# TypeScript code style preferences

**Scope: TypeScript only.** These are TS/JS nitpicks, not general code style — Ky works in other
languages and none of this transfers. Preferences for another language belong in their own
`code-style-<language>.md`, and absent such a file, follow the conventions of the code at hand.
Cross-language preferences are in `code-style-general.md`.


## `!!x` for presence checks, never `Boolean(x)`

Write `const hasFoo = !!foo`. Not `Boolean(foo)`, and not a verbose `(foo ?? '') !== ''` / `foo != null && foo !== ''`.

**Why:** it is Ky's stated preference, and it is also the technically correct choice. TypeScript (4.4+) carries an *aliased condition* through a `const` as a type guard, so a later `if (hasFoo)` narrows `foo` from `string | null | undefined` to `string`. Measured on tsc 5.8.3 with `--strict`:

| form | narrows? |
| --- | --- |
| `const h = !!foo` | yes |
| `const h = foo != null && foo !== ''` | yes |
| `const h = Boolean(foo)` | **no** — compile error at the narrowed use site |
| `let h = foo != null && foo !== ''` | **no** — the alias must be `const` |

`Boolean(x)` is an ordinary call returning `boolean`, so the alias carries no narrowing information — the same reason `arr.filter(Boolean)` does not narrow. Swapping `!!` for `Boolean()` as a "tidy-up" therefore turns working code into a build error that needs a non-null assertion to fix.

**How to apply:** default to `!!x`. If a reviewer or linter pushes toward `Boolean(x)`, leave a comment at the site noting the narrowing trap — that is the shape someone will otherwise rewrite it into. Don't reach for the verbose comparison form either: it narrows, but it's longer.

## Union types: trivial types or named declared types only

Each variant of a union must be either a trivial type (string/number literal, primitive) or a named declared type. **Never inline a complex object shape as a union member.**

```typescript
// ✗ inline shapes in the union
export type Notification =
  | { kind: 'email'; to: string; subject: string; body: string; replyTo?: string }
  | { kind: 'webhook'; url: string; payload: unknown; retries: number }

// ✓ named variants, trivial union
export interface EmailNotification { /* … */ }
export interface WebhookNotification { /* … */ }
export type Notification = EmailNotification | WebhookNotification
```

**Why:** Ky called this out as a review nit — *"I prefer to only have union types that are composed of trivial types or other declared types."* Each variant gets its own grep-able name, its own doc comment, and the union itself becomes a one-liner that documents the choice.

**How to apply:** when introducing or extending any union with complex variants, declare each variant as its own `interface` or `type` (PascalCase, descriptive) **before** writing the union, so the union fits on one line. Applies to any union, not just discriminated ones.
