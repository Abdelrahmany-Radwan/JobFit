# Contributing

Thanks for taking an interest in JobFit.

## Development workflow

1. Create a focused branch from `main`.
2. Keep each change scoped to one concern.
3. Run the Python syntax checks and test the public application in a local HTTP server.
4. Open a pull request that explains the problem, the implementation, and how the change was verified.
5. Merge only after automated checks pass.

## Project conventions

- Keep resume evidence traceable to user-provided text.
- Do not add generated qualifications or claims.
- Preserve client-side processing for resume contents unless a change explicitly documents a different privacy model.
- Prefer accessible, dependency-light browser code.
- Keep public-facing copy focused on the user problem and product behavior.

## Commit style

Use short, imperative commit subjects that describe the change, for example:

- `Improve document parsing feedback`
- `Add semantic-match regression test`
- `Refine mobile results layout`

Avoid combining unrelated changes in one commit.
