ISSUES:
------------
- Script now worked live, however, sometimes now the cookie script leads to a 400 page at Proshop. So valid cookie only sometimes gained even after cloudflare solved.

TODO:
------------
- Measure performance of each step in ms and see if optimization is needed
- Wenn active scheint alter Proshop Link in cookie script zu Proshop Warenkorb zu führen. Trick: Falls is_active = true aber keine URL, dann alternativ altem Link folgen?
- Understand session management from cookie script to purchase script (purchase uses last available from cookie script?)
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
