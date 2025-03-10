use std::error::Error;
use std::time::{Duration, Instant};
use serde_json::Value;
use chrono::Local;
use log::{info, warn, error};
use reqwest;

use crate::launch_purchase::{launch_purchase, should_attempt_purchase, PurchaseConfig};

/// Checks if a product is available by examining its directPurchaseLink
pub fn check_product_availability(product: &Value, default_link_5070: &str, default_link_5080: &str, default_link_5090: &str) -> (String, bool, String) {
    // Extract the product display name
    let display_name = product["displayName"].as_str().unwrap_or("Unknown Product");
    let mut purchase_link = String::new();
    
    // Check if the product has retailers
    let retailers = match product["retailers"].as_array() {
        Some(retailers) => retailers,
        None => return (display_name.to_string(), false, purchase_link)
    };
    
    // Check each retailer for a direct purchase link
    for retailer in retailers {
        let link = match retailer["directPurchaseLink"].as_str() {
            Some(link) => link,
            None => continue
        };
        
        purchase_link = link.to_string();
        
        // If the link is not one of the default values, the product is available
        if link != default_link_5070 && link != default_link_5080 && link != default_link_5090 {
            return (display_name.to_string(), true, purchase_link);
        }
    }
    
    (display_name.to_string(), false, purchase_link)
}

/// Configuration struct needed for API requests
pub struct ApiConfig {
    pub url: String,
    pub headers: HeadersConfig,
    pub default_links: DefaultLinksConfig,
    pub request: RequestConfig,
}

pub struct HeadersConfig {
    pub user_agent: String,
    pub accept: String,
    pub accept_language: String,
    pub connection: String,
    pub cache_control: String,
    pub pragma: String,
    pub sec_fetch_dest: String,
    pub sec_fetch_mode: String,
    pub sec_fetch_site: String,
    pub origin: String,
    pub referer: String,
    pub sec_ch_ua: String,
    pub sec_ch_ua_mobile: String,
    pub sec_ch_ua_platform: String,
}

pub struct DefaultLinksConfig {
    pub rtx_5070: String,
    pub rtx_5080: String,
    pub rtx_5090: String,
}

/// Accounts for request configuration timeout_ fields which are unused in this file 
#[allow(dead_code)]
pub struct RequestConfig {
    pub timeout_secs: u64,
    pub connect_timeout_secs: u64,
    pub max_attempts: u32,
    pub sleep_ms_min: u64,
    pub sleep_ms_max: u64,
}

/// Makes a request to NVIDIA API and checks product availability
pub async fn check_nvidia_api(
    config: &ApiConfig, 
    client: &reqwest::Client,
    purchase_config: &PurchaseConfig,
    cycle: u64
) -> Result<(), Box<dyn Error>> {
    let start_time = Instant::now();
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    
    info!("Cycle #{} - Starting API check at {}", cycle, timestamp);
    println!("\n[{}] Cycle #{} - Checking NVIDIA API...", timestamp, cycle);
    
    // Maximum number of attempts
    let max_attempts = config.request.max_attempts;
    let mut last_error = None;
    
    // Try the request with retries
    for attempt in 1..=max_attempts {
        if attempt > 1 {
            let backoff_secs = 2_u64.pow((attempt - 1) as u32);
            info!("Cycle #{} - Waiting {} seconds before retry (attempt {}/{})", cycle, backoff_secs, attempt, max_attempts);
            println!("[{}] Cycle #{} - Waiting {} seconds before retry (attempt {}/{})", 
                     Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, backoff_secs, attempt, max_attempts);
            tokio::time::sleep(Duration::from_secs(backoff_secs)).await;
        }
        
        // Build request with detailed headers
        let request = client.get(&config.url)
            .header("Accept", &config.headers.accept)
            .header("Accept-Language", &config.headers.accept_language)
            .header("Connection", &config.headers.connection)
            .header("Cache-Control", &config.headers.cache_control)
            .header("Pragma", &config.headers.pragma)
            .header("Sec-Fetch-Dest", &config.headers.sec_fetch_dest)
            .header("Sec-Fetch-Mode", &config.headers.sec_fetch_mode)
            .header("Sec-Fetch-Site", &config.headers.sec_fetch_site)
            .header("Origin", &config.headers.origin)
            .header("Referer", &config.headers.referer)
            .header("sec-ch-ua", &config.headers.sec_ch_ua)
            .header("sec-ch-ua-mobile", &config.headers.sec_ch_ua_mobile)
            .header("sec-ch-ua-platform", &config.headers.sec_ch_ua_platform);
        
        // Send the request
        let request_start = Instant::now();
        let response_result = request.send().await;
        let response_time = request_start.elapsed().as_millis();
            
        // Handle request errors
        let response = match response_result {
            Ok(response) => response,
            Err(e) => {
                let msg = format!("Request error: {}", e);
                error!("Cycle #{} - {}", cycle, msg);
                println!("[{}] Cycle #{} - {}", 
                        Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                last_error = Some(msg);
                continue;
            }
        };
        
        let status = response.status();
        info!("Cycle #{} - Response status: {}, Time: {}ms", cycle, status, response_time);
        
        // Check if response is successful
        if !status.is_success() {
            let msg = format!("HTTP error status: {} ({})", status, status.canonical_reason().unwrap_or("Unknown"));
            error!("Cycle #{} - {}", cycle, msg);
            println!("[{}] Cycle #{} - {}", 
                    Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
            last_error = Some(msg);
            continue;
        }
        
        // Get response bytes
        let bytes = match response.bytes().await {
            Ok(bytes) => bytes,
            Err(e) => {
                let msg = format!("Error reading response body: {}", e);
                error!("Cycle #{} - {}", cycle, msg);
                println!("[{}] Cycle #{} - {}", 
                        Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                last_error = Some(msg);
                continue;
            }
        };
        
        let response_length = bytes.len();
        info!("Cycle #{} - Successfully received response with length: {} bytes", cycle, response_length);
        
        // Parse JSON
        let json = match serde_json::from_slice::<serde_json::Value>(&bytes) {
            Ok(json) => json,
            Err(e) => {
                let msg = format!("Couldn't parse response as JSON: {}", e);
                error!("Cycle #{} - {}", cycle, msg);
                println!("[{}] Cycle #{} - {}", 
                        Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                last_error = Some(msg);
                continue;
            }
        };
        
        let mut product_statuses = Vec::new();
        
        // Extract searched products
        let searched_products = match json["searchedProducts"].as_object() {
            Some(searched_products) => searched_products,
            None => {
                let msg = "searchedProducts not found in the response";
                warn!("Cycle #{} - {}", cycle, msg);
                println!("[{}] Cycle #{} - {}", 
                        Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                last_error = Some(msg.to_string());
                continue;
            }
        };
        
        // Extract product details
        let product_details = match searched_products.get("productDetails") {
            Some(product_details) => product_details,
            None => {
                let msg = "productDetails not found in the response";
                warn!("Cycle #{} - {}", cycle, msg);
                println!("[{}] Cycle #{} - {}", 
                        Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                last_error = Some(msg.to_string());
                continue;
            }
        };
        
        // Extract products array
        let products = match product_details.as_array() {
            Some(products) => products,
            None => {
                let msg = "productDetails is not an array";
                warn!("Cycle #{} - {}", cycle, msg);
                println!("[{}] Cycle #{} - {}", 
                        Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                last_error = Some(msg.to_string());
                continue;
            }
        };
        
        // Check if products array is empty
        if products.is_empty() {
            let msg = "No products found in the API response.";
            warn!("Cycle #{} - {}", cycle, msg);
            println!("[{}] Cycle #{} - {}", 
                    Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
            last_error = Some(msg.to_string());
            continue;
        }
        
        // Process each product
        for product in products {
            let (name, available, link) = check_product_availability(
                product, 
                &config.default_links.rtx_5070,
                &config.default_links.rtx_5080,
                &config.default_links.rtx_5090
            );
            let status = if available { "AVAILABLE" } else { "NOT AVAILABLE" };
            
            // If product is available and should be purchased, launch purchase process
            if available && should_attempt_purchase(&name, purchase_config) {
                info!("Cycle #{} - Product '{}' is available, launching purchase process", cycle, name);
                println!("[{}] Cycle #{} - Product '{}' is available, launching purchase process", 
                        Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, name);
                
                // Launch the purchase process
                if let Err(e) = launch_purchase(&name, &link).await {
                    error!("Cycle #{} - Failed to launch purchase for '{}': {}", cycle, name, e);
                    println!("[{}] Cycle #{} - ❌ Failed to launch purchase for '{}': {}", 
                            Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, name, e);
                }
            }
            
            product_statuses.push((name, status.to_string()));
        }
        
        // Print and log the results
        let total_time = start_time.elapsed().as_millis();
        let status_summary: Vec<String> = product_statuses
            .iter()
            .map(|(name, status)| format!("{}: {}", name, status))
            .collect();
        
        let summary = format!(
            "[{}] Cycle #{} - Status: SUCCESS ({}), Products: [{}], Response Length: {} bytes, Response Time: {}ms, Total Time: {}ms",
            Local::now().format("%Y-%m-%d %H:%M:%S"),
            cycle,
            status,
            status_summary.join(", "),
            response_length,
            response_time,
            total_time
        );
        
        println!("{}", summary);
        info!("{}", summary);
        
        return Ok(());
    }
    
    // If we get here, all attempts failed
    let error_msg = last_error.unwrap_or_else(|| "All requests failed with unknown errors".to_string());
    let total_time = start_time.elapsed().as_millis();
    
    let summary = format!(
        "[{}] Cycle #{} - Status: FAILED, Error: {}, Response Length: 0 bytes, Response Time: 0ms, Total Time: {}ms",
        Local::now().format("%Y-%m-%d %H:%M:%S"),
        cycle,
        error_msg,
        total_time
    );
    
    println!("{}", summary);
    error!("{}", summary);
    
    Err(error_msg.into())
}

/// For testing purposes only: Simulates a product being available
pub async fn simulate_available_product(product_name: &str, purchase_config: &crate::launch_purchase::PurchaseConfig, force_error: bool) -> Result<(), Box<dyn Error>> {
    println!("\n[{}] 🧪 TEST MODE: Simulating product availability for '{}'", 
             Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
    
    // Check if this product should trigger a purchase based on configuration
    if !crate::launch_purchase::should_attempt_purchase(product_name, purchase_config) {
        println!("[{}] 🧪 TEST MODE: Product '{}' would not trigger a purchase (not in configured product list)", 
                 Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
        return Ok(());
    }
    
    // Simulate the product being available
    println!("[{}] 🧪 TEST MODE: Product '{}' is available, launching purchase process", 
             Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
    
    // Use a realistic purchase URL for testing - the one that works with the standalone Python script
    let purchase_url = if force_error {
        // Invalid URL to force an error
        "https://invalid-url-to-force-error"
    } else {
        "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D"
    };
    
    // Launch the purchase process with the test URL
    match crate::launch_purchase::launch_purchase(product_name, purchase_url).await {
        Ok(_) => {
            println!("[{}] 🧪 TEST MODE: ✅ Purchase successfully launched for '{}'", 
                     Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
        },
        Err(e) => {
            println!("[{}] 🧪 TEST MODE: ❌ Failed to launch purchase for '{}': {}", 
                     Local::now().format("%Y-%m-%d %H:%M:%S"), product_name, e);
        }
    }
    
    Ok(())
}
