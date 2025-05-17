# Changelog

## [3.1.1] - 2025-05-16

### Changed
- Bumped `markdown` dependency to 3.8
- Refactored custom Markdown extensions to remove `md_globals`, use `register()`, and adjust processor priorities for compatibility with markdown >=3.4.0
