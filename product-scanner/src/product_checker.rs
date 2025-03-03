use serde_json::Value;

/// Checks if a product is available by examining its directPurchaseLink
pub fn check_product_availability(product: &Value, default_link_5080: &str, default_link_5090: &str) -> (String, bool) {
    // Extract the product display name
    let display_name = product["displayName"].as_str().unwrap_or("Unknown Product");
    
    // Check if the product has retailers
    if let Some(retailers) = product["retailers"].as_array() {
        for retailer in retailers {
            if let Some(link) = retailer["directPurchaseLink"].as_str() {
                // Check if the link is one of the default values
                if link != default_link_5080 && link != default_link_5090 {
                    return (display_name.to_string(), true);
                }
            }
        }
    }
    
    (display_name.to_string(), false)
}
