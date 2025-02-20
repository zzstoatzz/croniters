use pyo3::prelude::*;

#[pyfunction]
pub fn is_32bit() -> bool {
    // Method 1: Check pointer size.
    // If the size of a pointer is 32 bits, we're on a 32-bit system.
    let bits = std::mem::size_of::<usize>() * 8;

    // Method 2: Use compile-time architecture constant.
    // `std::env::consts::ARCH` returns a string describing the target architecture.
    // The following choices are heuristically chosen to represent common 32-bit architectures:
    // - "x86": Generally indicates 32-bit Intel/AMD architectures.
    // - "arm": Refers to 32-bit ARM; note that 64-bit ARM is usually "aarch64".
    // - "mips": Commonly denotes a 32-bit MIPS architecture.
    // - "powerpc": Typically represents 32-bit PowerPC; 64-bit is often "powerpc64".
    // These assumptions may need revisiting if new architectures are encountered.
    let arch = std::env::consts::ARCH;

    // Method 3: Check maximum usize value.
    // If `usize::MAX` fits within 32 bits, it suggests a 32-bit system.
    let is_maxsize_small = usize::MAX == 0xFFFF_FFFF;

    bits == 32 || matches!(arch, "x86" | "arm" | "mips" | "powerpc") || is_maxsize_small
}

#[pyfunction]
pub fn is_leap(year: i32) -> bool {
    year % 400 == 0 || (year % 4 == 0 && year % 100 != 0)
}
