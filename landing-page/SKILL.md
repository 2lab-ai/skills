---
name: landing-page
description: Use when the user asks to build or redesign a landing page, product page, launch page, marketing page, or founder/personal page — as a standalone HTML file or as a page inside an existing app or site repo. Args: the target (site, repo + path, URL path, framework, delivery URL) and an optional theme name.
---

# landing-page

The entrypoint for every landing-page request in this repository. It does two
things and nothing else: it pins down **where the page has to ship**, and it
routes to the **theme workflow** that builds it.

The rules and craft live in the theme workflow and its references. Do not
restate them here.

## 1. Target contract (fill before writing any markup)

A landing page is only done when it appears where the user expects it. Record
these, each with the evidence you read it from (`file:line`, a command output,
or a direct user quote) — unknowns stay `UNKNOWN`, never a guess:

| Field | Meaning |
|---|---|
| **Site** | The product/person the page is for. |
| **Repo + path** | The repository and directory the page lives in. `UNKNOWN` if the user has not named one. |
| **Route** | The URL path it serves (`/`, `/launch`, `/products/x`), or `file://` for a standalone deliverable. |
| **Framework / stack** | Read from the target repo, not assumed — e.g. `package.json`, the router directory layout, the CSS system in use. |
| **Preserved behavior** | What must keep working after the change: existing routes, layout/shell, analytics, i18n, SEO metadata, CI gates. |
| **Delivery URL** | Where the user will look at the result (preview deployment, dev server, or the file path). |
| **Lane** | §2. |

If **Repo + path**, **Framework / stack**, or **Delivery URL** is `UNKNOWN` for
a page the user described as live, resolve it before implementing — the answer
changes the lane, and the lane changes everything downstream.

## 2. Lanes

| Lane | When | What it means |
|---|---|---|
| **A — existing app** | The target is a route inside a real application or site repo. | Build it in that repo's actual stack (its framework, router, component and styling conventions). Its own build/lint/type/test gates are the gates. The standalone HTML validator does not apply. |
| **B — standalone** | The deliverable is a self-contained page: a one-off file, a demo, an example, a page with no host app. | One standalone `.html` file, no build step. The theme's standalone validator applies. |

Choose the lane from the target contract, not from convenience.

**Unreachable live target:** if the user points at a live site or route that
this repository cannot reach — no repo access, no known stack, no deploy path —
say so and report the specific missing piece (repo URL, branch, stack, deploy
credentials). **Do not ship a standalone HTML file, a skill example, or a
screenshot as a substitute for the app route that was asked for**, and do not
claim the live page changed.

## 3. Theme routing

| The request | Route to |
|---|---|
| Names a registered theme | That theme's workflow in the table below. |
| Names no theme | [`workflows/editorial-machine.md`](workflows/editorial-machine.md) — the default. |
| Names an unregistered theme ("brutalist", "unknown-theme") | **Stop and ask** which registered theme to use, or register the new one first. Never silently substitute the default. |

### Registered themes

| Theme | Workflow | Requires |
|---|---|---|
| `editorial-machine` *(default)* | [`workflows/editorial-machine.md`](workflows/editorial-machine.md) | The sibling `editorial-machine/` skill directory, installed alongside this one. |
| `mono-instrument` (also named by "mono", "monochrome", "모노") | [`workflows/mono-instrument.md`](workflows/mono-instrument.md) | The sibling `mono-instrument/` skill directory, installed alongside this one. |

Each row exists because its theme exists. A row here is
a promise that the workflow file is on disk; `tests/test_contract.py` fails on
a row that names a file this repo does not ship.

### Registering a new theme

1. Add `workflows/<theme>.md` with: required reading, the build steps, the
   per-lane gates, and the output contract. Cite the theme's references —
   do not copy them into the workflow.
2. Add one row to **Registered themes** naming the workflow and its
   dependencies.
3. Run `python3 -m unittest discover -s landing-page/tests -v`.

## 4. Installation note

This skill resolves its workflows and their sibling assets by relative path.
Install the whole repository (or at minimum this directory **and** every
registered theme's directory) into the same skills directory. `landing-page`
alone cannot build anything.
