# Coding Rules

## General Style

- Write clean, readable, production-oriented code.
- Use English for code, comments, identifiers, filenames, and commit messages.
- Prefer DRY code.
- Follow SRP, but do not split code into tiny unnecessary abstractions.
- Prefer simple, maintainable solutions over clever ones.
- Avoid premature optimization, but do optimize hot paths when repeated often.
- Keep functions small enough to understand, but not artificially fragmented.
- Use explicit names. Avoid vague names like `data`, `temp`, `stuff` unless context is obvious.
- Handle errors intentionally. Do not silently swallow exceptions.
- Avoid hardcoding project-specific values unless explicitly requested.

## Python Rules

- Prefer Python 3.13-compatible code unless the project specifies otherwise.
- Use type hints where they improve clarity.
- Use `dataclass` or `pydantic` only when they reduce complexity.
- Prefer standard library first.
- Avoid global mutable state unless necessary.
- Keep side effects explicit.
- Separate pure logic from IO/control code where practical.
- Prefer `pathlib.Path` over raw string paths.
- Prefer clear exceptions over returning ambiguous `None`.
- For scripts, provide a clean `main()` entrypoint.

## Performance & IO

- For repeated operations, prefer in-memory processing.
- Avoid unnecessary disk IO.
- For repeated capture flows such as ADB screenshots, UI dumps, logs, or image processing:
  - keep data in RAM when possible
  - only write artifacts when debugging, explicitly requested, or necessary
  - avoid writing temporary files in tight loops
- If temporary files are unavoidable, prefer RAM-backed locations such as `/tmp` on systems where it is tmpfs.
- Do not save screenshots/UI dumps/logs by default unless the task requires it.
