# Invariants

The hard rules that must never be broken. Each has a stable ID so other docs can reference it as a digest. If a task seems to require breaking one, stop and escalate — do not work around it silently.

A rule earns a place here only if breaking it causes damage that is expensive or impossible to undo: data loss, a security hole, a broken contract others depend on. Preferences and conventions belong in [[CLAUDE]], not here.

## <TODO: category — e.g. data isolation>

- **INV-001 — <TODO: the rule, stated as an absolute>.** <TODO: what it means concretely, and how it is enforced or tested.>
- **INV-002 — <TODO>.** <TODO>

## <TODO: category — e.g. auth & credentials>

- **INV-010 — <TODO>.** <TODO>

## Business logic — marketplace-analytics

The rules specific to this project's domain. They sit on top of the categories above.

- **INV-050 — <TODO>.** <TODO>

## Related

- [[docs/agent-toolbox]] — the tools you use while respecting these rules
- [[docs/overview]] — the system these rules govern
