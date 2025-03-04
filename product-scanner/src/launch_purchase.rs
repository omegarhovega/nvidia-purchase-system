use log::info;
use chrono::Local;
use std::error::Error;
use std::process::Command;
use crate::sound::play_error_alert;

/// Configuration for the purchase launcher
pub struct PurchaseConfig {
    pub enabled: bool,
    pub product_names: Vec<String>,
}

/// Launches the purchase process for a specific product
/// 
/// This integrates with the purchase-core component by calling the Python purchase_method.py script
pub async fn launch_purchase(product_name: &str, product_link: &str) -> Result<(), Box<dyn Error>> {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    
    // Log the purchase attempt
    info!("PURCHASE ATTEMPT - Product: {}, Link: {}", product_name, product_link);
    println!("[{}] 🚀 LAUNCHING PURCHASE PROCESS FOR: {}", timestamp, product_name);
    println!("[{}] 🔗 Product Link: {}", timestamp, product_link);
    
    // Call the Python purchase_method.py script with the product link
    println!("[{}] ⏳ Starting purchase process with purchase_method.py", timestamp);
    
    // Find the absolute path to the Python script
    let purchase_script_path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .ok_or("Failed to get parent directory")?
        .join("purchase-core")
        .join("src")
        .join("purchase_method.py");
    
    info!("Running Python script: {:?}", purchase_script_path);
    
    // Execute the Python script with the product link as an argument
    let output = Command::new("python")
        .arg(&purchase_script_path)
        .arg(product_link)  // Pass the product link as a command-line argument
        .output()?;
    
    // Log the output
    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        info!("Purchase script executed successfully: {}", stdout);
        println!("[{}] ✅ Purchase process completed successfully", timestamp);
        println!("[{}] Output: {}", timestamp, stdout);
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        info!("Purchase script failed: {}", stderr);
        println!("[{}] ❌ Purchase process failed", timestamp);
        println!("[{}] Error: {}", timestamp, stderr);
        play_error_alert();
        return Err(format!("Purchase script failed: {}", stderr).into());
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
