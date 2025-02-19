# croniters

A fast, Rust-powered cron expression parser and iterator for Python.

## Overview

`croniters` is a drop-in replacement for the Python `croniter` package, implemented in Rust using the battle-tested `cron` crate. It provides efficient cron expression parsing and iteration while maintaining API compatibility with `croniter`.

## Why?

- **Performance**: Rust implementation provides significant performance improvements
- **Reliability**: Built on proven Rust crates (`cron` and `chrono`)
- **Compatibility**: Drop-in replacement for `croniter`
- **Maintenance**: Simpler codebase by leveraging existing Rust ecosystem

## Implementation Plan

### Phase 1: Core Functionality

Initial implementation focusing on the most commonly used features:

- Basic cron expression parsing
- `get_next()`/`get_prev()` methods
- DateTime/timestamp conversions
- Support for basic cron formats (5-field Unix cron)

### Phase 2: Extended Features

Add support for:

- Second and year fields (6 and 7-field formats)
- Hash-based expressions
- Range iteration (`croniter_range`)
- All croniter expression aliases (@yearly, @monthly, etc)

### Phase 3: Full Compatibility

Complete feature parity with croniter:

- All edge cases and special syntax
- Full timezone support
- Complete test suite port

## Technical Stack

- **Cron Parsing**: `cron` crate
- **DateTime Handling**: `chrono` crate
- **Python Bindings**: `pyo3`
- **Build System**: `maturin`

## Development Status

🚧 Currently in early development

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

Same as croniter - MIT License 