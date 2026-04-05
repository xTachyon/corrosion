mod imp;

#[unsafe(no_mangle)]
pub fn f(x: u32, y: u32) -> u32 {
    x + y + 6
}
