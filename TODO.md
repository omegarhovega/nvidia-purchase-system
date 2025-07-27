ISSUES/OBSERVATIONS:
------------
- Script now worked live, however, sometimes now the cookie script leads to a 400 page at Proshop. So valid cookie only sometimes gained even after cloudflare solved.
- Old purchase links seem to work as well (sometimes when cards were live, the cookie script presumably using an old purchase link led to carting of itmes as well)

TODO:
------------
- Measure performance of each step in ms and see if optimization is needed
- Add automatic update to skus when change is detected via early-warning in product-scanner (default.toml files)
- Add purchase mechanism for all products


For a release build with better performance:
cargo build --release
$env:RUST_LOG="info"
.\target\release\nvidia-fe-monitor

# API Links (adjust in config > default.toml)
https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PROFESHOP5090&locale=de-de
https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PRO5080FESHOP&locale=de-de
https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PRONVGFT570SHOP&locale=de-de

https://api.nvidia.partners/edge/product/search?page=1&limit=9&manufacturer_filter=NVIDIA%7E1&category=GPU&locale=de-de&manufacturer=NVIDIA
