---
name: frontend-ux-palette-system
description: "Use when improving a frontend's UX, visual system, color palette, or design consistency. Read the complete frontend first, choose one evidence-backed palette, apply it consistently across all pages, and clearly label the result as AI-generated without inventing facts."
argument-hint: "Describe the frontend UX or visual consistency goal"
user-invocable: true
disable-model-invocation: false
---

# Frontend UX Palette System

## Purpose

Create a grounded, product-wide UX and visual update for an existing frontend. The workflow produces one coherent palette and applies it consistently across shared components, application chrome, and every routed page. It must distinguish verified repository facts from design recommendations and must present the design decision as AI-generated.

## When to Use

Use this skill when the request includes any of the following:

- Improve frontend UX or visual consistency
- Choose or change a product color palette
- Apply one design system across all pages
- Review an existing React, Vue, Svelte, or HTML frontend before redesigning it
- Remove mixed colors, inconsistent components, or one-off visual treatments
- Make a dashboard, SaaS console, admin tool, or developer tool more usable

Do not use it for backend-only work, API changes, or isolated non-visual refactors.

## Non-Negotiable Rules

1. **Read before deciding.** Inspect the complete frontend source surface before selecting a palette or proposing page-level changes.
2. **Use repository evidence.** Treat package files, routes, shared components, CSS, and page content as facts. Do not infer product requirements that are not present.
3. **Choose one palette.** After selection, do not mix competing primary palettes. Semantic status colors may remain distinct for success, warning, and error states.
4. **Use semantic tokens.** Centralize primary, accent, background, surface, text, muted text, border, focus, warning, and danger colors. Avoid adding raw primary hex values to individual pages.
5. **Preserve behavior.** UX improvements must not change API contracts, navigation IDs, data meaning, or domain logic unless explicitly requested.
6. **Label provenance.** Every design-system report or generated UX recommendation must include the exact label `AI-generated design system` and identify which parts are repository facts versus recommendations.
7. **Respect accessibility.** Preserve visible focus, keyboard operation, readable contrast, touch targets, reduced-motion preferences, responsive reflow, and non-color status cues.
8. **Validate.** Run the frontend's narrowest available build, typecheck, lint, or test command after edits. Report failures honestly.

## Procedure

### 1. Establish Scope and Stack

- Identify the workspace root and frontend root.
- Read the frontend package manifest and determine the actual framework, styling system, build tool, and available icon/font dependencies.
- Read the app entry point and route/navigation registry.
- Do not assume React, Tailwind, Bootstrap, or any library until the repository confirms it.

### 2. Read the Complete Frontend

Inventory source files with the workspace file search or an equivalent read-only command. Read all relevant frontend files before making a visual decision:

- `package.json`, lockfile, build config, TypeScript/config files
- HTML entry and global CSS
- App shell, routing, navigation, sidebar, header, footer
- All shared components
- Every routed screen/page/view
- Existing design tokens, theme files, icon/font imports, and responsive styles

Record only observed facts:

- Product/domain language and user workflow
- Number and names of routes/pages
- Existing spacing, typography, colors, radii, shadows, and interaction patterns
- Shared components and duplicated visual rules
- Known accessibility or responsive risks

If the frontend is too large to read in one pass, split it into deterministic batches and finish the inventory before choosing a palette. Never fill unread sections with assumptions.

### 3. Generate and Verify One Palette

If the UI/UX Pro Max skill or its local search script is available, run one product-specific design-system search using 2–5 meaningful terms and the detected stack. For an operational developer/QA console, query terms should reflect the observed product, such as `developer tool QA automation dashboard SaaS`.

Verify the result before applying it:

- Confirm the returned product/style/category matches the repository.
- Prefer an operational, readable palette over decorative or marketing-oriented output.
- Reject palettes that create poor contrast, excessive purple/indigo bias, or conflict with existing semantic status colors.
- Keep exactly one primary, one primary-dark/hover, one accent, one background, one surface, one muted surface, one text, one muted text, one border, one focus color, one warning, and one danger token.
- If the search is unavailable or returns no relevant result, use the built-in accessibility and product-type rules as a fallback and explicitly state that it is a fallback.

Before editing, write a short decision record:

```text
AI-generated design system
Repository facts: <observed product, stack, routes, and existing visual constraints>
Chosen direction: <style and rationale>
Palette: <token name>: <value> ...
Accessibility checks: <contrast/focus/responsive considerations>
Rejected alternatives: <brief reason>
```

### 4. Apply the System in the Smallest Safe Layers

Edit in this order:

1. Global CSS/theme tokens, body background, typography, focus, and reduced-motion rules.
2. Shared buttons, badges, empty states, inputs, cards, and icon primitives.
3. App shell, sidebar, header, navigation, and persistent status indicators.
4. Each routed page, replacing stale primary treatments with semantic tokens.
5. Responsive layout fixes for dense grids, tables, long IDs, badges, and code blocks.

Use the existing framework and component patterns. Do not install a UI library merely to imitate an example from another framework. Do not rewrite domain logic or introduce a new abstraction unless it removes repeated visual logic.

For icons:

- Use one consistent icon family already present in the project or a verified project dependency.
- Do not use emoji as interface icons.
- Give icon-only controls an accessible name; mark decorative icons appropriately.

For status colors:

- Keep success, warning, and failure distinguishable by text/icon as well as color.
- Do not reuse the primary palette as a substitute for semantic status colors.

### 5. Validate the Whole Frontend

Run, in order:

1. The frontend production build or typecheck.
2. Editor diagnostics for all changed files, if available.
3. A source scan for competing primary colors, duplicated raw palette values, missing focus states, and emoji interface icons.
4. Responsive checks at approximately 375px, 768px, 1024px, and 1440px when browser tooling is available.

If a validation fails, repair the same slice and rerun the same check before widening scope. Do not claim completion when a command was not run.

### 6. Report the Result

The final report must be concise and include:

- The exact label `AI-generated design system`
- Repository facts used
- The single palette selected and where its tokens live
- Shared components and pages updated
- Validation commands and outcomes
- Any unresolved limitation or unverified browser check

## Completion Checklist

- [ ] Complete frontend inventory finished before palette selection
- [ ] Framework and styling stack verified from repository files
- [ ] One palette selected and documented as AI-generated
- [ ] Semantic tokens centralized
- [ ] Shared components use tokens
- [ ] App shell and every routed page use the same primary system
- [ ] Status colors retain semantic meaning and text/icon cues
- [ ] No emoji used as interface icons
- [ ] Focus indicators are visible
- [ ] Reduced motion is respected
- [ ] Dense layouts reflow without horizontal page overflow
- [ ] Long IDs and labels can wrap or expose their full value
- [ ] Build/typecheck/diagnostics completed and honestly reported
