/// CRC-32 over a byte slice, the checksum the v2 readers verify.
pub fn checksum(data: &[u8]) -> u32 {
    data.iter().fold(0xFFFF_FFFFu32, |crc, &b| {
        let mut c = crc ^ u32::from(b);
        for _ in 0..8 {
            c = if c & 1 == 1 { (c >> 1) ^ 0xEDB8_8320 } else { c >> 1 };
        }
        c
    }) ^ 0xFFFF_FFFF
}

#[allow(dead_code, reason = "kept for the v1 readers until they migrate to checksum")]
fn legacy_checksum(data: &[u8]) -> u32 {
    data.iter().fold(0u32, |sum, &b| sum.wrapping_add(u32::from(b)))
}

#[allow(dead_code, reason = "called only from the simd module, which builds under the simd feature")]
fn fast_checksum(data: &[u8]) -> u32 {
    checksum(data)
}
