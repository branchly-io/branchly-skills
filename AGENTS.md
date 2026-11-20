# Agent Guidelines

## This repository is public

Keep every contribution clean:

- The commit history and PR description tell the story. Do not add narrating comments to pull requests.
- Never put internal links, internal task IDs, or production analytics details into commits, PR descriptions, or comments.
- Base every statement on what is committed: code, docs, commit messages, and the PR description.

## Skill authoring

- Follow the [Agent Skills specification](https://agentskills.io/specification): `name` matching the folder, trigger-based `description`, `license`, and `metadata`.
- Every skill carries `metadata: {author: branchly-io, version: "X.Y.Z"}` and bumps its version in any PR that changes it (see "Versioning" in the README).
- Before documenting `branchly_*` MCP calls, verify the tool's current signature against the live branchly MCP server when available — names, parameters, and enum values. Do not rely on memory or examples copied from other skills.
