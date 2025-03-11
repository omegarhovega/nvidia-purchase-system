- Check that purchase link/mechanics are correct
- Unify log in main python coordinator
- Add sounds (beep) when purchase is successful (through python file and not at all interfering with rust)
- Measure performance of each step in ms and see if optimization is needed
- Monitor with changes to other API endpoint with alert:
https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=Pro5090FE&locale=DE
{"success":true,"map":null,"listMap":[{"is_active":"false","product_url":"","price":"1000000","fe_sku":"Pro5090FE_DE","locale":"DE"}]}

Ok, can you write a separate minimal script in rust that checks the https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=Pro5090FE&locale=DE endpoint.

An expected reply is {"success":true,"map":null,"listMap":[{"is_active":"false","product_url":"","price":"1000000","fe_sku":"Pro5090FE_DE","locale":"DE"}]}

I want the script to provide an alert when any of product_url, is_active and fe_sku change from their values as given above. You can use reqwest and the same headers as in product_checker

For a release build with better performance:
cargo build --release
$env:RUST_LOG="info"
.\target\release\nvidia-fe-monitor