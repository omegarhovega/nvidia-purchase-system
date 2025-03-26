- Measure performance of each step in ms and see if optimization is needed
- session manager messages are not logged correctly in coordinator + no sound alerts when session manager fails
- Run early-warning separately to get alert when sku changes and drop is imminent (https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PROFESHOP5090&locale=DE" response changes to {"success":true,"map":null,"listMap":[]})

For a release build with better performance:
cargo build --release
$env:RUST_LOG="info"
.\target\release\nvidia-fe-monitor

- NL example link: https://www.proshop.nl/NVIDIA-Exclusive-Store/NVIDIA-GeForce-RTX-5090-Founders-Edition-32GB-1-stuks-per-klant/3331529 it seems that after alert is triggered that new sku is made (early-warning) one can follow the old purchase link?


https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PRONVGFT570SHOP&locale=de-de

{"success":true,"map":null,"listMap":[{"is_active":"false","product_url":"","price":"1000000","fe_sku":"PRONVGFT570SHOP_DE","locale":"DE"}]}
changed to this when active: {"success":true,"map":null,"listMap":[{"is_active":"true","product_url":"","price":"619","fe_sku":"PRONVGFT570SHOP_DE","locale":"DE"}]}

Antworten der API hier aufzeichnen, um zu checken welcher link erscheint (product_url)
gleiches für
https://api.nvidia.partners/edge/product/search?page=1&limit=9&manufacturer_filter=NVIDIA%7E1&category=GPU&locale=de-de&manufacturer=NVIDIA

und direct link felder directPurchaseLink, internalLink

https://www.proshop.de/Basket?cid=a4c6bafe-965b-48cf-bdcc-9556aef2986f

Ich hatte gerade die API verfolgt - als die Karten verfügbar waren, hat API gemeldet: {"success":true,"map":null,"listMap":[{"is_active":"true","product_url":"","price":"619","fe_sku":"PRONVGFT570SHOP_DE","locale":"DE"}]}
Yannik — 14:40
Jupp
Veritas — 14:40
Aber kein Link - erscheint der nie?
Yannik — 14:41
Doch der erscheint
Veritas — 14:41
Ah, dann aber nur für Bruchteile von Sekunden 🙂
Yannik — 14:41
Eigentlich wird er immer angezeigt, wenn Active True ist
Hast du manuell abgefragt oder mit einem Script? 🙂