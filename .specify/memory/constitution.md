# MCP Jamovi Constitution

Version: 1.0.0
Status: Active
Date: 2026-04-27

## Purpose

This constitution defines the non-negotiable principles for all Spec-Driven Development work in this repository. It governs every specification, plan, task list, and implementation generated for MCP Jamovi.

## Articles

### Article I: Spec First
Specifications are the source of truth. Code exists to implement accepted specifications, not to define them.

### Article II: Test Before Code
Implementation work must be traceable to tests, acceptance criteria, or explicit validation steps. No feature proceeds without a verifiable definition of done.

### Article III: Minimal Surface Area
Prefer the smallest possible set of modules, files, and abstractions that satisfy the current feature.

### Article IV: Preserve Domain Boundaries
Keep jamovi analysis contracts, R execution, and GUI translation separate. Do not merge them into a single opaque layer.

### Article V: Headless and Deterministic
All server behavior must remain headless, reproducible, and safe for automated execution.

### Article VI: Contract-Driven Inputs
Validate all external inputs against explicit schemas before any execution or side effect.

### Article VII: Session Reuse
If a feature requires repeated analysis on the same dataset, prefer explicit session reuse over repeated reloads.

### Article VIII: Error Clarity
Surface failures as actionable messages with stable codes and suggested next actions.

### Article IX: Documentation Traceability
Every implementation must trace back to a spec, a plan, and a task list. The artifact chain must stay current with the code.

## Operating Rules

- Create or update the spec before changing behavior.
- Create or update the plan before designing implementation details.
- Create or update the task list before editing code.
- Keep feature folders isolated by scope.
- Use the same artifact names across features for consistency.

## Amendment Policy

Changes to this constitution require a documented rationale and an explicit review of impact on existing specs and tasks.
