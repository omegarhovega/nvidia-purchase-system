- Measure performance of each step in ms and see if optimization is needed
- session manager messages are not logged correctly in coordinator + no sound alerts when session manager fails

For a release build with better performance:
cargo build --release
$env:RUST_LOG="info"
.\target\release\nvidia-fe-monitor