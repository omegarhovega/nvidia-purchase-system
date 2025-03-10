use log::info;
use chrono::Local;
use std::error::Error;
use crate::execute_purchase;

/// Configuration for the purchase launcher
pub struct PurchaseConfig {
    pub enabled: bool,
    pub product_names: Vec<String>,
}

/// Launches the purchase process for a specific product
/// 
/// This integrates with the execute_purchase module directly
pub async fn launch_purchase(product_name: &str, product_link: &str) -> Result<(), Box<dyn Error>> {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    
    // Log the purchase attempt
    info!("PURCHASE ATTEMPT - Product: {}, Link: {}", product_name, product_link);
    println!("[{}] 🚀 LAUNCHING PURCHASE PROCESS FOR: {}", timestamp, product_name);
    println!("[{}] 🔗 Product Link: {}", timestamp, product_link);
    
    // Call the execute_purchase module with the product link
    println!("[{}] ⏳ Starting purchase process with execute_purchase", timestamp);
    
    info!("Running fast_purchase function with link: {}", product_link);
    
    // Execute the purchase function with the product link
    match execute_purchase::fast_purchase(product_link) {
        Ok(true) => {
            info!("Purchase executed successfully");
            println!("[{}] ✅ Purchase process completed successfully", timestamp);
        },
        Ok(false) => {
            info!("Purchase process failed");
            println!("[{}] ❌ Purchase process failed", timestamp);
            return Err("Purchase process failed".into());
        },
        Err(e) => {
            info!("Purchase process error: {}", e);
            println!("[{}] ❌ Purchase process failed with error", timestamp);
            println!("[{}] Error: {}", timestamp, e);
            return Err(e);
        }
    }
    
    Ok(())
}

/// Determines if a purchase should be attempted for a given product
pub fn should_attempt_purchase(product_name: &str, config: &PurchaseConfig) -> bool {
    if !config.enabled {
        return false;
    }
    
    // Check if this product is in our list of products to purchase
    config.product_names.iter().any(|name| product_name.contains(name))
}
