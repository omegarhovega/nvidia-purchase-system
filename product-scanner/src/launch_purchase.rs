use log::info;
use chrono::Local;
use std::error::Error;
use crate::execute_purchase;
use tokio::time;

/// Launches the purchase process for a specific product
/// 
/// This integrates with the execute_purchase module directly
pub async fn launch_purchase(product_name: &str, product_link: &str) -> Result<(), Box<dyn Error>> {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    
    // Log the purchase attempt
    info!("PURCHASE ATTEMPT - Product: {}, Link: {}", product_name, product_link);
    println!("[{}] 🚀 LAUNCHING PURCHASE PROCESS FOR: {}", timestamp, product_name);
    println!("[{}] 🔗 Product Link: {}", timestamp, product_link);
    
    // Make multiple purchase attempts in quick succession
    const MAX_ATTEMPTS: usize = 3;
    let mut success = false;
    let mut last_error: Option<Box<dyn Error>> = None;
    
    for attempt in 1..=MAX_ATTEMPTS {
        println!("[{}] ⏳ Starting purchase attempt {}/{}", timestamp, attempt, MAX_ATTEMPTS);
        info!("Running fast_purchase function with link: {} (attempt {}/{})", product_link, attempt, MAX_ATTEMPTS);
        
        // Execute the purchase function with the product link
        match execute_purchase::fast_purchase(product_link) {
            Ok(true) => {
                info!("Purchase executed successfully on attempt {}", attempt);
                println!("[{}] ✅ Purchase process completed successfully on attempt {}", timestamp, attempt);
                success = true;
                break;
            },
            Ok(false) => {
                info!("Purchase process failed on attempt {}", attempt);
                println!("[{}] ⚠️ Purchase attempt {} failed, trying again...", timestamp, attempt);
                last_error = Some("Purchase process failed".into());
                
                // Only wait between attempts, not after the last one
                if attempt < MAX_ATTEMPTS {
                    time::sleep(time::Duration::from_millis(500)).await;
                }
            },
            Err(e) => {
                info!("Purchase process error on attempt {}: {}", attempt, e);
                println!("[{}] ⚠️ Purchase attempt {} failed with error: {}", timestamp, attempt, e);
                last_error = Some(e);
                
                // Only wait between attempts, not after the last one
                if attempt < MAX_ATTEMPTS {
                    time::sleep(time::Duration::from_millis(500)).await;
                }
            }
        }
    }
    
    if success {
        Ok(())
    } else if let Some(e) = last_error {
        println!("[{}] ❌ All {} purchase attempts failed", timestamp, MAX_ATTEMPTS);
        Err(e)
    } else {
        Err("All purchase attempts failed with unknown error".into())
    }
}