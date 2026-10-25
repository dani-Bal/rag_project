# Coding guidelines

## Naming

Use `snake_case` for functions, variables, and modules; `PascalCase` for classes; and
`UPPER_SNAKE_CASE` for constants. Keep code, identifiers, comments, and docstrings in English.

## Documentation

Use Google-style docstrings for public functions, public classes, and public methods with
non-obvious behavior. Describe behavior, arguments, return values, and relevant exceptions where
useful. Trivial private helpers do not need redundant docstrings.

## Functions and classes

Prefer small, focused functions and composition. Avoid deep nesting, unnecessary inheritance, and
abstraction layers without a concrete need.

## Error handling and logging

Catch specific exceptions, provide useful error messages, and never expose credentials. Do not
silently suppress errors. Use Python's `logging` module rather than `print()` for application logs,
with appropriate log levels and without sensitive content.

## Configuration

Keep configuration centralized in `rag_project.config`, use `pydantic-settings` for environment
values, and keep API keys outside source code.
