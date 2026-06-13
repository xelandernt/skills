---
name: rust-best-practices
description: >
  Comprehensive Rust coding guidelines with 179 references across 14 categories.
  Use when writing, reviewing, or refactoring Rust code. Covers ownership,
  error handling, async patterns, API design, memory optimization, performance,
  testing, and common anti-patterns.
---

# Rust Best Practices

Comprehensive guide for writing high-quality, idiomatic, and highly optimized Rust code. Contains 179 references across 14 categories, prioritized by impact to guide agents in code generation and refactoring.

## When to Apply

Reference these guidelines when:
- Writing new Rust functions, structs, or modules
- Implementing error handling or async code
- Designing public APIs for libraries
- Reviewing code for ownership/borrowing issues
- Optimizing memory usage or reducing allocations
- Tuning performance for hot paths
- Refactoring existing Rust code

## Reference Categories by Priority

| Priority | Category              | Impact    | Prefix   | References |
|----------|-----------------------|-----------|----------|------------|
| 1        | Ownership & Borrowing | CRITICAL  | `own-`   | 12         |
| 2        | Error Handling        | CRITICAL  | `err-`   | 12         |
| 3        | Memory Optimization   | CRITICAL  | `mem-`   | 15         |
| 4        | API Design            | HIGH      | `api-`   | 15         |
| 5        | Async/Await           | HIGH      | `async-` | 15         |
| 6        | Compiler Optimization | HIGH      | `opt-`   | 12         |
| 7        | Naming Conventions    | MEDIUM    | `name-`  | 16         |
| 8        | Type Safety           | MEDIUM    | `type-`  | 10         |
| 9        | Testing               | MEDIUM    | `test-`  | 13         |
| 10       | Documentation         | MEDIUM    | `doc-`   | 11         |
| 11       | Performance Patterns  | MEDIUM    | `perf-`  | 11         |
| 12       | Project Structure     | LOW       | `proj-`  | 11         |
| 13       | Clippy & Linting      | LOW       | `lint-`  | 11         |
| 14       | Anti-patterns         | REFERENCE | `anti-`  | 15         |

---

## Quick Reference

### 1. Ownership & Borrowing (CRITICAL)

- [`own-borrow-over-clone`](references/own-borrow-over-clone.md) - Prefer `&T` borrowing over `.clone()`
- [`own-slice-over-vec`](references/own-slice-over-vec.md) - Accept `&[T]` not `&Vec<T>`, `&str` not `&String`
- [`own-cow-conditional`](references/own-cow-conditional.md) - Use `Cow<'a, T>` for conditional ownership
- [`own-arc-shared`](references/own-arc-shared.md) - Use `Arc<T>` for thread-safe shared ownership
- [`own-rc-single-thread`](references/own-rc-single-thread.md) - Use `Rc<T>` for single-threaded sharing
- [`own-refcell-interior`](references/own-refcell-interior.md) - Use `RefCell<T>` for interior mutability (single-thread)
- [`own-mutex-interior`](references/own-mutex-interior.md) - Use `Mutex<T>` for interior mutability (multi-thread)
- [`own-rwlock-readers`](references/own-rwlock-readers.md) - Use `RwLock<T>` when reads dominate writes
- [`own-copy-small`](references/own-copy-small.md) - Derive `Copy` for small, trivial types
- [`own-clone-explicit`](references/own-clone-explicit.md) - Make `Clone` explicit, avoid implicit copies
- [`own-move-large`](references/own-move-large.md) - Move large data instead of cloning
- [`own-lifetime-elision`](references/own-lifetime-elision.md) - Rely on lifetime elision when possible

### 2. Error Handling (CRITICAL)

- [`err-thiserror-lib`](references/err-thiserror-lib.md) - Use `thiserror` for library error types
- [`err-anyhow-app`](references/err-anyhow-app.md) - Use `anyhow` for application error handling
- [`err-result-over-panic`](references/err-result-over-panic.md) - Return `Result`, don't panic on expected errors
- [`err-context-chain`](references/err-context-chain.md) - Add context with `.context()` or `.with_context()`
- [`err-no-unwrap-prod`](references/err-no-unwrap-prod.md) - Never use `.unwrap()` in production code
- [`err-expect-bugs-only`](references/err-expect-bugs-only.md) - Use `.expect()` only for programming errors
- [`err-question-mark`](references/err-question-mark.md) - Use `?` operator for clean propagation
- [`err-from-impl`](references/err-from-impl.md) - Use `#[from]` for automatic error conversion
- [`err-source-chain`](references/err-source-chain.md) - Use `#[source]` to chain underlying errors
- [`err-lowercase-msg`](references/err-lowercase-msg.md) - Error messages: lowercase, no trailing punctuation
- [`err-doc-errors`](references/err-doc-errors.md) - Document errors with `# Errors` section
- [`err-custom-type`](references/err-custom-type.md) - Create custom error types, not `Box<dyn Error>`

### 3. Memory Optimization (CRITICAL)

- [`mem-with-capacity`](references/mem-with-capacity.md) - Use `with_capacity()` when size is known
- [`mem-smallvec`](references/mem-smallvec.md) - Use `SmallVec` for usually-small collections
- [`mem-arrayvec`](references/mem-arrayvec.md) - Use `ArrayVec` for bounded-size collections
- [`mem-box-large-variant`](references/mem-box-large-variant.md) - Box large enum variants to reduce type size
- [`mem-boxed-slice`](references/mem-boxed-slice.md) - Use `Box<[T]>` instead of `Vec<T>` when fixed
- [`mem-thinvec`](references/mem-thinvec.md) - Use `ThinVec` for often-empty vectors
- [`mem-clone-from`](references/mem-clone-from.md) - Use `clone_from()` to reuse allocations
- [`mem-reuse-collections`](references/mem-reuse-collections.md) - Reuse collections with `clear()` in loops
- [`mem-avoid-format`](references/mem-avoid-format.md) - Avoid `format!()` when string literals work
- [`mem-write-over-format`](references/mem-write-over-format.md) - Use `write!()` instead of `format!()` 
- [`mem-arena-allocator`](references/mem-arena-allocator.md) - Use arena allocators for batch allocations
- [`mem-zero-copy`](references/mem-zero-copy.md) - Use zero-copy patterns with slices and `Bytes`
- [`mem-compact-string`](references/mem-compact-string.md) - Use `CompactString` for small string optimization
- [`mem-smaller-integers`](references/mem-smaller-integers.md) - Use smallest integer type that fits
- [`mem-assert-type-size`](references/mem-assert-type-size.md) - Assert hot type sizes to prevent regressions

### 4. API Design (HIGH)

- [`api-builder-pattern`](references/api-builder-pattern.md) - Use Builder pattern for complex construction
- [`api-builder-must-use`](references/api-builder-must-use.md) - Add `#[must_use]` to builder types
- [`api-newtype-safety`](references/api-newtype-safety.md) - Use newtypes for type-safe distinctions
- [`api-typestate`](references/api-typestate.md) - Use typestate for compile-time state machines
- [`api-sealed-trait`](references/api-sealed-trait.md) - Seal traits to prevent external implementations
- [`api-extension-trait`](references/api-extension-trait.md) - Use extension traits to add methods to foreign types
- [`api-parse-dont-validate`](references/api-parse-dont-validate.md) - Parse into validated types at boundaries
- [`api-impl-into`](references/api-impl-into.md) - Accept `impl Into<T>` for flexible string inputs
- [`api-impl-asref`](references/api-impl-asref.md) - Accept `impl AsRef<T>` for borrowed inputs
- [`api-must-use`](references/api-must-use.md) - Add `#[must_use]` to `Result` returning functions
- [`api-non-exhaustive`](references/api-non-exhaustive.md) - Use `#[non_exhaustive]` for future-proof enums/structs
- [`api-from-not-into`](references/api-from-not-into.md) - Implement `From`, not `Into` (auto-derived)
- [`api-default-impl`](references/api-default-impl.md) - Implement `Default` for sensible defaults
- [`api-common-traits`](references/api-common-traits.md) - Implement `Debug`, `Clone`, `PartialEq` eagerly
- [`api-serde-optional`](references/api-serde-optional.md) - Gate `Serialize`/`Deserialize` behind feature flag

### 5. Async/Await (HIGH)

- [`async-tokio-runtime`](references/async-tokio-runtime.md) - Use Tokio for production async runtime
- [`async-no-lock-await`](references/async-no-lock-await.md) - Never hold `Mutex`/`RwLock` across `.await`
- [`async-spawn-blocking`](references/async-spawn-blocking.md) - Use `spawn_blocking` for CPU-intensive work
- [`async-tokio-fs`](references/async-tokio-fs.md) - Use `tokio::fs` not `std::fs` in async code
- [`async-cancellation-token`](references/async-cancellation-token.md) - Use `CancellationToken` for graceful shutdown
- [`async-join-parallel`](references/async-join-parallel.md) - Use `tokio::join!` for parallel operations
- [`async-try-join`](references/async-try-join.md) - Use `tokio::try_join!` for fallible parallel ops
- [`async-select-racing`](references/async-select-racing.md) - Use `tokio::select!` for racing/timeouts
- [`async-bounded-channel`](references/async-bounded-channel.md) - Use bounded channels for backpressure
- [`async-mpsc-queue`](references/async-mpsc-queue.md) - Use `mpsc` for work queues
- [`async-broadcast-pubsub`](references/async-broadcast-pubsub.md) - Use `broadcast` for pub/sub patterns
- [`async-watch-latest`](references/async-watch-latest.md) - Use `watch` for latest-value sharing
- [`async-oneshot-response`](references/async-oneshot-response.md) - Use `oneshot` for request/response
- [`async-joinset-structured`](references/async-joinset-structured.md) - Use `JoinSet` for dynamic task groups
- [`async-clone-before-await`](references/async-clone-before-await.md) - Clone data before await, release locks

### 6. Compiler Optimization (HIGH)

- [`opt-inline-small`](references/opt-inline-small.md) - Use `#[inline]` for small hot functions
- [`opt-inline-always-rare`](references/opt-inline-always-rare.md) - Use `#[inline(always)]` sparingly
- [`opt-inline-never-cold`](references/opt-inline-never-cold.md) - Use `#[inline(never)]` for cold paths
- [`opt-cold-unlikely`](references/opt-cold-unlikely.md) - Use `#[cold]` for error/unlikely paths
- [`opt-likely-hint`](references/opt-likely-hint.md) - Use `likely()`/`unlikely()` for branch hints
- [`opt-lto-release`](references/opt-lto-release.md) - Enable LTO in release builds
- [`opt-codegen-units`](references/opt-codegen-units.md) - Use `codegen-units = 1` for max optimization
- [`opt-pgo-profile`](references/opt-pgo-profile.md) - Use PGO for production builds
- [`opt-target-cpu`](references/opt-target-cpu.md) - Set `target-cpu=native` for local builds
- [`opt-bounds-check`](references/opt-bounds-check.md) - Use iterators to avoid bounds checks
- [`opt-simd-portable`](references/opt-simd-portable.md) - Use portable SIMD for data-parallel ops
- [`opt-cache-friendly`](references/opt-cache-friendly.md) - Design cache-friendly data layouts (SoA)

### 7. Naming Conventions (MEDIUM)

- [`name-types-camel`](references/name-types-camel.md) - Use `UpperCamelCase` for types, traits, enums
- [`name-variants-camel`](references/name-variants-camel.md) - Use `UpperCamelCase` for enum variants
- [`name-funcs-snake`](references/name-funcs-snake.md) - Use `snake_case` for functions, methods, modules
- [`name-consts-screaming`](references/name-consts-screaming.md) - Use `SCREAMING_SNAKE_CASE` for constants/statics
- [`name-lifetime-short`](references/name-lifetime-short.md) - Use short lowercase lifetimes: `'a`, `'de`, `'src`
- [`name-type-param-single`](references/name-type-param-single.md) - Use single uppercase for type params: `T`, `E`, `K`, `V`
- [`name-as-free`](references/name-as-free.md) - `as_` prefix: free reference conversion
- [`name-to-expensive`](references/name-to-expensive.md) - `to_` prefix: expensive conversion
- [`name-into-ownership`](references/name-into-ownership.md) - `into_` prefix: ownership transfer
- [`name-no-get-prefix`](references/name-no-get-prefix.md) - No `get_` prefix for simple getters
- [`name-is-has-bool`](references/name-is-has-bool.md) - Use `is_`, `has_`, `can_` for boolean methods
- [`name-iter-convention`](references/name-iter-convention.md) - Use `iter`/`iter_mut`/`into_iter` for iterators
- [`name-iter-method`](references/name-iter-method.md) - Name iterator methods consistently
- [`name-iter-type-match`](references/name-iter-type-match.md) - Iterator type names match method
- [`name-acronym-word`](references/name-acronym-word.md) - Treat acronyms as words: `Uuid` not `UUID`
- [`name-crate-no-rs`](references/name-crate-no-rs.md) - Crate names: no `-rs` suffix

### 8. Type Safety (MEDIUM)

- [`type-newtype-ids`](references/type-newtype-ids.md) - Wrap IDs in newtypes: `UserId(u64)`
- [`type-newtype-validated`](references/type-newtype-validated.md) - Newtypes for validated data: `Email`, `Url`
- [`type-enum-states`](references/type-enum-states.md) - Use enums for mutually exclusive states
- [`type-option-nullable`](references/type-option-nullable.md) - Use `Option<T>` for nullable values
- [`type-result-fallible`](references/type-result-fallible.md) - Use `Result<T, E>` for fallible operations
- [`type-phantom-marker`](references/type-phantom-marker.md) - Use `PhantomData<T>` for type-level markers
- [`type-never-diverge`](references/type-never-diverge.md) - Use `!` type for functions that never return
- [`type-generic-bounds`](references/type-generic-bounds.md) - Add trait bounds only where needed
- [`type-no-stringly`](references/type-no-stringly.md) - Avoid stringly-typed APIs, use enums/newtypes
- [`type-repr-transparent`](references/type-repr-transparent.md) - Use `#[repr(transparent)]` for FFI newtypes

### 9. Testing (MEDIUM)

- [`test-cfg-test-module`](references/test-cfg-test-module.md) - Use `#[cfg(test)] mod tests { }`
- [`test-use-super`](references/test-use-super.md) - Use `use super::*;` in test modules
- [`test-integration-dir`](references/test-integration-dir.md) - Put integration tests in `tests/` directory
- [`test-descriptive-names`](references/test-descriptive-names.md) - Use descriptive test names
- [`test-arrange-act-assert`](references/test-arrange-act-assert.md) - Structure tests as arrange/act/assert
- [`test-proptest-properties`](references/test-proptest-properties.md) - Use `proptest` for property-based testing
- [`test-mockall-mocking`](references/test-mockall-mocking.md) - Use `mockall` for trait mocking
- [`test-mock-traits`](references/test-mock-traits.md) - Use traits for dependencies to enable mocking
- [`test-fixture-raii`](references/test-fixture-raii.md) - Use RAII pattern (Drop) for test cleanup
- [`test-tokio-async`](references/test-tokio-async.md) - Use `#[tokio::test]` for async tests
- [`test-should-panic`](references/test-should-panic.md) - Use `#[should_panic]` for panic tests
- [`test-criterion-bench`](references/test-criterion-bench.md) - Use `criterion` for benchmarking
- [`test-doctest-examples`](references/test-doctest-examples.md) - Keep doc examples as executable tests

### 10. Documentation (MEDIUM)

- [`doc-all-public`](references/doc-all-public.md) - Document all public items with `///`
- [`doc-module-inner`](references/doc-module-inner.md) - Use `//!` for module-level documentation
- [`doc-examples-section`](references/doc-examples-section.md) - Include `# Examples` with runnable code
- [`doc-errors-section`](references/doc-errors-section.md) - Include `# Errors` for fallible functions
- [`doc-panics-section`](references/doc-panics-section.md) - Include `# Panics` for panicking functions
- [`doc-safety-section`](references/doc-safety-section.md) - Include `# Safety` for unsafe functions
- [`doc-question-mark`](references/doc-question-mark.md) - Use `?` in examples, not `.unwrap()`
- [`doc-hidden-setup`](references/doc-hidden-setup.md) - Use `# ` prefix to hide example setup code
- [`doc-intra-links`](references/doc-intra-links.md) - Use intra-doc links: `[Vec]`
- [`doc-link-types`](references/doc-link-types.md) - Link related types and functions in docs
- [`doc-cargo-metadata`](references/doc-cargo-metadata.md) - Fill `Cargo.toml` metadata

### 11. Performance Patterns (MEDIUM)

- [`perf-iter-over-index`](references/perf-iter-over-index.md) - Prefer iterators over manual indexing
- [`perf-iter-lazy`](references/perf-iter-lazy.md) - Keep iterators lazy, collect() only when needed
- [`perf-collect-once`](references/perf-collect-once.md) - Don't `collect()` intermediate iterators
- [`perf-entry-api`](references/perf-entry-api.md) - Use `entry()` API for map insert-or-update
- [`perf-drain-reuse`](references/perf-drain-reuse.md) - Use `drain()` to reuse allocations
- [`perf-extend-batch`](references/perf-extend-batch.md) - Use `extend()` for batch insertions
- [`perf-chain-avoid`](references/perf-chain-avoid.md) - Avoid `chain()` in hot loops
- [`perf-collect-into`](references/perf-collect-into.md) - Use `collect_into()` for reusing containers
- [`perf-black-box-bench`](references/perf-black-box-bench.md) - Use `black_box()` in benchmarks
- [`perf-release-profile`](references/perf-release-profile.md) - Optimize release profile settings
- [`perf-profile-first`](references/perf-profile-first.md) - Profile before optimizing

### 12. Project Structure (LOW)

- [`proj-lib-main-split`](references/proj-lib-main-split.md) - Keep `main.rs` minimal, logic in `lib.rs`
- [`proj-mod-by-feature`](references/proj-mod-by-feature.md) - Organize modules by feature, not type
- [`proj-flat-small`](references/proj-flat-small.md) - Keep small projects flat
- [`proj-mod-rs-dir`](references/proj-mod-rs-dir.md) - Use `mod.rs` for multi-file modules
- [`proj-pub-crate-internal`](references/proj-pub-crate-internal.md) - Use `pub(crate)` for internal APIs
- [`proj-pub-super-parent`](references/proj-pub-super-parent.md) - Use `pub(super)` for parent-only visibility
- [`proj-pub-use-reexport`](references/proj-pub-use-reexport.md) - Use `pub use` for clean public API
- [`proj-prelude-module`](references/proj-prelude-module.md) - Create `prelude` module for common imports
- [`proj-bin-dir`](references/proj-bin-dir.md) - Put multiple binaries in `src/bin/`
- [`proj-workspace-large`](references/proj-workspace-large.md) - Use workspaces for large projects
- [`proj-workspace-deps`](references/proj-workspace-deps.md) - Use workspace dependency inheritance

### 13. Clippy & Linting (LOW)

- [`lint-deny-correctness`](references/lint-deny-correctness.md) - `#![deny(clippy::correctness)]`
- [`lint-warn-suspicious`](references/lint-warn-suspicious.md) - `#![warn(clippy::suspicious)]`
- [`lint-warn-style`](references/lint-warn-style.md) - `#![warn(clippy::style)]`
- [`lint-warn-complexity`](references/lint-warn-complexity.md) - `#![warn(clippy::complexity)]`
- [`lint-warn-perf`](references/lint-warn-perf.md) - `#![warn(clippy::perf)]`
- [`lint-pedantic-selective`](references/lint-pedantic-selective.md) - Enable `clippy::pedantic` selectively
- [`lint-missing-docs`](references/lint-missing-docs.md) - `#![warn(missing_docs)]`
- [`lint-unsafe-doc`](references/lint-unsafe-doc.md) - `#![warn(clippy::undocumented_unsafe_blocks)]`
- [`lint-cargo-metadata`](references/lint-cargo-metadata.md) - `#![warn(clippy::cargo)]` for published crates
- [`lint-rustfmt-check`](references/lint-rustfmt-check.md) - Run `cargo fmt --check` in CI
- [`lint-workspace-lints`](references/lint-workspace-lints.md) - Configure lints at workspace level

### 14. Anti-patterns (REFERENCE)

- [`anti-unwrap-abuse`](references/anti-unwrap-abuse.md) - Don't use `.unwrap()` in production code
- [`anti-expect-lazy`](references/anti-expect-lazy.md) - Don't use `.expect()` for recoverable errors
- [`anti-clone-excessive`](references/anti-clone-excessive.md) - Don't clone when borrowing works
- [`anti-lock-across-await`](references/anti-lock-across-await.md) - Don't hold locks across `.await`
- [`anti-string-for-str`](references/anti-string-for-str.md) - Don't accept `&String` when `&str` works
- [`anti-vec-for-slice`](references/anti-vec-for-slice.md) - Don't accept `&Vec<T>` when `&[T]` works
- [`anti-index-over-iter`](references/anti-index-over-iter.md) - Don't use indexing when iterators work
- [`anti-panic-expected`](references/anti-panic-expected.md) - Don't panic on expected/recoverable errors
- [`anti-empty-catch`](references/anti-empty-catch.md) - Don't use empty `if let Err(_) = ...` blocks
- [`anti-over-abstraction`](references/anti-over-abstraction.md) - Don't over-abstract with excessive generics
- [`anti-premature-optimize`](references/anti-premature-optimize.md) - Don't optimize before profiling
- [`anti-type-erasure`](references/anti-type-erasure.md) - Don't use `Box<dyn Trait>` when `impl Trait` works
- [`anti-format-hot-path`](references/anti-format-hot-path.md) - Don't use `format!()` in hot paths
- [`anti-collect-intermediate`](references/anti-collect-intermediate.md) - Don't `collect()` intermediate iterators
- [`anti-stringly-typed`](references/anti-stringly-typed.md) - Don't use strings for structured data

---

## Recommended Cargo.toml Settings

```toml
[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true

[profile.bench]
inherits = "release"
debug = true
strip = false

[profile.dev]
opt-level = 0
debug = true

[profile.dev.package."*"]
opt-level = 3  # Optimize dependencies in dev
```

---

## How to Use

This skill provides reference identifiers for quick lookup. When generating or reviewing Rust code:

1. **Check relevant category** based on task type
2. **Apply references** with matching prefix
3. **Prioritize** CRITICAL > HIGH > MEDIUM > LOW
4. **Read reference files** in `references/` for detailed examples

### Reference Application by Task

| Task                | Primary Categories      |
|---------------------|-------------------------|
| New function        | `own-`, `err-`, `name-` |
| New struct/API      | `api-`, `type-`, `doc-` |
| Async code          | `async-`, `own-`        |
| Error handling      | `err-`, `api-`          |
| Memory optimization | `mem-`, `own-`, `perf-` |
| Performance tuning  | `opt-`, `mem-`, `perf-` |
| Code review         | `anti-`, `lint-`        |

---

## Sources

This skill synthesizes best practices from:
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [Rust Design Patterns](https://rust-unofficial.github.io/patterns/)
- Production codebases: ripgrep, tokio, serde, polars, axum, deno
- Clippy lint documentation
- Community conventions (2024-2025)
