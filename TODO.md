- Measure performance of each step in ms and see if optimization is needed
- session manager messages are not logged correctly in coordinator + no sound alerts when session manager fails
- Run early-warning separately to get alert when sku changes and drop is imminent (https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PROFESHOP5090&locale=DE" response changes to {"success":true,"map":null,"listMap":[]})

For a release build with better performance:
cargo build --release
$env:RUST_LOG="info"
.\target\release\nvidia-fe-monitor

- NL example link: https://www.proshop.nl/NVIDIA-Exclusive-Store/NVIDIA-GeForce-RTX-5090-Founders-Edition-32GB-1-stuks-per-klant/3331529 it seems that after alert is triggered that new sku is made (early-warning) one can follow the old purchase link?