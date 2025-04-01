ISSUES:
------------
- Why in logs did product_url not appear in product_checker request response but in early-warning responses? Check that current solution gets link with next drop (could also be rate cached response?) --> the product_url should not be empty here when is_active is true, this happened with the monitor responses, not with the early-warning responses - check headers, other details carefully. Add cache busting or new session for each monitoring request?
- Why is launch_purchase so much slower than fast_purchase?

TODO:
------------
- SIMPLIFY:Remove launch_purchase.rs file (test purchase simulate_available_product 3 secs slower than fast_purchase) and launch purchase directly with minimal delay
- Measure performance of each step in ms and see if optimization is needed
- Ensure right logging, with time stamps for everything
- Wenn active scheint alter Proshop Link in cookie script zu Proshop Warenkorb zu führen. Trick: Falls is_active = true aber keine URL, dann alternativ altem Link folgen?
- Understand session management from cookie script to purchase script (purchase uses last available from cookie script?)
- Add purchase mechanism for all products


For a release build with better performance:
cargo build --release
$env:RUST_LOG="info"
.\target\release\nvidia-fe-monitor


https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PRONVGFT570SHOP&locale=de-de

{"success":true,"map":null,"listMap":[{"is_active":"false","product_url":"","price":"1000000","fe_sku":"PRONVGFT570SHOP_DE","locale":"DE"}]}
changed to this when active: {"success":true,"map":null,"listMap":[{"is_active":"true","product_url":"","price":"619","fe_sku":"PRONVGFT570SHOP_DE","locale":"DE"}]}
--> the product_url should not be empty here when is_active is true, this happened with the monitor responses, not with the early-warning responses - check headers, other details carefully.

https://api.nvidia.partners/edge/product/search?page=1&limit=9&manufacturer_filter=NVIDIA%7E1&category=GPU&locale=de-de&manufacturer=NVIDIA

und direct link felder directPurchaseLink, internalLink

https://www.proshop.de/Basket?cid=a4c6bafe-965b-48cf-bdcc-9556aef2986f


!!!!!!! WHY does the execute-purchase run in 0.56s but when doing the test from the scanner it takes 3.59s? It seems the launch_purchase functionality causes 3 sec delay?! Drop and just call fast_purchase directly.

Example:
PS C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system> cd product-scanner
PS C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\product-scanner> cargo run --bin execute-purchase
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.28s
     Running `target\debug\execute-purchase.exe`
[INFO] Loading cookies from C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_cookies.json
[INFO] Loaded 18 cookies from C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_cookies.json
[INFO] Found cf_clearance cookie: aNLkQdEB_a...
[INFO] Making request to https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D
[INFO] Final URL after redirects: https://marketplace.nvidia.com/de-de/consumer/
[INFO] Saved final page HTML to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\final_page_rs.html
[INFO] Saved redirect history to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\redirect_history_rs.json
[INFO] Saved cookies to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_purchase_cookies_2025-03-30_13-14-46_vfulZi8U.json
[INFO] Found ASP.NET_SessionId cookie: mzkvxtth51syjtwxm0qrz1hm
[INFO] Request completed with status 200 OK in 0.56s
[INFO] Purchase attempt completed successfully!

PS C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\product-scanner> cargo run --bin product-scanner -- --test
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.20s
     Running `target\debug\product-scanner.exe --test`
[2025-03-30 13:17:25] Configuration loaded successfully
[2025-03-30 13:17:25] Running in TEST MODE

[2025-03-30 13:17:25] 🧪 TEST MODE: Simulating product availability for 'GeForce RTX 5090'
[2025-03-30 13:17:25] 🔗 Using sample URL for testing: https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=bFHncOsrkXFbYRF56H68bUYIDb5AcZcdMLlBR44dZW46fqwfc5XdgVX7GcBoTv0MPqdirRx3xR%2B%2BHzx%2BBotzaO%2F4L%2FlTqKPHplY5e9vGhWSXFRzoebTbYEhykPPVXJ4u2DB0yTMDccuO1cXeoNsy2MRNf3G9p3fUSVp9zASLJ0uJymzkdEijj0QKsZLS8I4GQ252Y7yAUFDboHiEt9TDvJ3Fo1HXw9KXeueIUZ432lQhBuzhHR78O9N%2FbJldC6r9YdeRgCszPH2m2u7VRaaZPasTuvylSd0yj7tOxQOTou85%2BV7D%2Fw3brZng%2Bc5t4CE6vL0qKGsyvL4lH%2FfCE3YWkQ%3D%3D
[2025-03-30 13:17:25] 🚀 LAUNCHING PURCHASE PROCESS FOR: GeForce RTX 5090
[2025-03-30 13:17:25] 🔗 Product Link: https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=bFHncOsrkXFbYRF56H68bUYIDb5AcZcdMLlBR44dZW46fqwfc5XdgVX7GcBoTv0MPqdirRx3xR%2B%2BHzx%2BBotzaO%2F4L%2FlTqKPHplY5e9vGhWSXFRzoebTbYEhykPPVXJ4u2DB0yTMDccuO1cXeoNsy2MRNf3G9p3fUSVp9zASLJ0uJymzkdEijj0QKsZLS8I4GQ252Y7yAUFDboHiEt9TDvJ3Fo1HXw9KXeueIUZ432lQhBuzhHR78O9N%2FbJldC6r9YdeRgCszPH2m2u7VRaaZPasTuvylSd0yj7tOxQOTou85%2BV7D%2Fw3brZng%2Bc5t4CE6vL0qKGsyvL4lH%2FfCE3YWkQ%3D%3D
[2025-03-30 13:17:25] ⏳ Starting purchase attempt 1/3
[INFO] Loading cookies from C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_cookies.json
[INFO] Loaded 18 cookies from C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_cookies.json
[INFO] Found cf_clearance cookie: aNLkQdEB_a...
[INFO] Making request to https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=bFHncOsrkXFbYRF56H68bUYIDb5AcZcdMLlBR44dZW46fqwfc5XdgVX7GcBoTv0MPqdirRx3xR%2B%2BHzx%2BBotzaO%2F4L%2FlTqKPHplY5e9vGhWSXFRzoebTbYEhykPPVXJ4u2DB0yTMDccuO1cXeoNsy2MRNf3G9p3fUSVp9zASLJ0uJymzkdEijj0QKsZLS8I4GQ252Y7yAUFDboHiEt9TDvJ3Fo1HXw9KXeueIUZ432lQhBuzhHR78O9N%2FbJldC6r9YdeRgCszPH2m2u7VRaaZPasTuvylSd0yj7tOxQOTou85%2BV7D%2Fw3brZng%2Bc5t4CE6vL0qKGsyvL4lH%2FfCE3YWkQ%3D%3D
[INFO] Final URL after redirects: https://marketplace.nvidia.com/de-de/consumer/
[INFO] Saved final page HTML to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\final_page_rs.html
[INFO] Saved redirect history to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\redirect_history_rs.json
[INFO] Saved cookies to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_purchase_cookies_2025-03-30_13-17-29_aUigxP39.json
[INFO] Found ASP.NET_SessionId cookie: mzkvxtth51syjtwxm0qrz1hm
[INFO] Request completed with status 200 OK in 3.59s
[2025-03-30 13:17:25] ✅ Purchase process completed successfully on attempt 1
[2025-03-30 13:17:29] Test completed, exiting
PS C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\product-scanner> 

