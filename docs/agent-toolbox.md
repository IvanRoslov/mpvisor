---
last-verified: 2026-11-19
canonical: true
---

# Agent toolbox — build, deploy & test marketplace-analytics

**Point an agent at this file** to give it the tools used to build, configure, deploy, and test the system. This is the canonical procedural reference for tool selection; playbooks link here for concrete commands.

> Ground every entry below in something real — a command you ran, a file in the repo, a
> tool you called. Mark anything unverified "(confirm in repo)" rather than guessing.

## 0. Environment at a glance

- Vault: `<TODO: org/repo of this knowledge base>` (this repo).
- Code: Docs and code share this repo. The vault is the root-level `*.md` files and `docs/`; everything else is code. A leaf's `Code:` line links the directory of this repo that holds the code for its facts.
- <TODO: the contract, guide, or standard this project must follow, if any.>

## 1. Build & run locally

```bash
<TODO: the real commands — install, run, health check.>
```

<TODO: what the local stack stands in for (databases, queues, third-party services), and
the one gotcha that bites newcomers.>

## 2. Deploy & configure

<TODO: how a change reaches staging and production. Name the mechanism (CI job, console,
CLI), the environments, and how environment variables are set — including when a change
takes effect. A missing variable failing silently is the classic time sink.>

## 3. Domain-specific tooling

<TODO: the stores and services the business logic runs on, and how to inspect them while
building — the queries, CLIs, and dashboards you actually use to see what happened.>

## 4. Tests

<TODO: unit, integration, e2e — the commands, where the logs land, and how to run a
single case. Note anything that skips silently.>

## 5. Verify the running system

<TODO: how to check a deployed change is really live — logs, metrics, a smoke request,
a browser check. Verify effects, not step statuses.>

## Related

- [[docs/invariants]] — the rules these tools must not be used to break
- [[docs/playbooks/README]] — runbooks that build on this toolbox
- [[docs/overview]] — what the system is
