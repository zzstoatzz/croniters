# croniters

a fast, rust-powered cron expression parser and iterator for Python.

## Overview

`croniters` intends to be a drop-in replacement for the python [`croniter`](https://github.com/kiorky/croniter) package, implemented in Rust.

> [!IMPORTANT]
> I say "intends to" because while the test suite is ported and should cover the majority of cases, there may be subtle differences between rust and python implementations.


## Why?
`croniter` is no longer maintained and everyone vendoring means more collective toil.

rust already has good datetime support and rust types are great for this sort of pedantry.

## Project Roadmap

- port everything to rust incrementally, maintaining the public `croniter` API.
- consider deprecating things that don't make coherent sense.

### Phase 0: Setup
- [x] get pyo3 setup
- [x] port test suite from croniter
- [ ] move constants and simple utils to rust

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

## (Planned) Technical Stack

- **Cron Parsing**: `cron` crate
- **Python Bindings**: `pyo3`
- **Build System**: `maturin`

## Contributing

Please do - I am only learning rust and pyo3! See the [justfile](justfile) for details on running locally.

## License

Same as croniter - MIT License 