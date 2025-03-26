use std::error::Error;
use std::time::Duration;
use chrono::Local;
use log::{info, warn, error};
use reqwest;
use serde::{Deserialize, Serialize};

use crate::launch_purchase::{launch_purchase, should_attempt_purchase, PurchaseConfig};

#[derive(Debug, Serialize, Deserialize)]
pub struct FeInventoryResponse {
    success: bool,
    map: Option<serde_json::Value>,
    #[serde(rename = "listMap")]
    list_map: Vec<FeProductInfo>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FeProductInfo {
    #[serde(rename = "is_active")]
    is_active: String,
    product_url: String,
    price: String,
    #[serde(rename = "fe_sku")]
    fe_sku: String,
    locale: String,
}

/// Configuration struct needed for API requests
pub struct ApiConfig {
    pub fe_inventory_url: String,
    pub headers: HeadersConfig,
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

pub struct RequestConfig {
    pub timeout_secs: u64,
    pub max_attempts: u32,
    pub sleep_ms_min: u64,
    pub sleep_ms_max: u64,
}

/// Makes a request to NVIDIA FE inventory API and checks product availability
pub async fn check_nvidia_api(
    config: &ApiConfig, 
    client: &reqwest::Client,
    purchase_config: &PurchaseConfig,
    cycle: u64
) -> Result<(), Box<dyn Error>> {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    info!("Cycle #{} - Starting FE inventory check at {}", cycle, timestamp);

    // Maximum number of attempts
    let max_attempts = config.request.max_attempts;
    let mut last_error = None;
    
    // Try the request with retries
    for attempt in 1..=max_attempts {
        if attempt > 1 {
            let backoff_secs = 2_u64.pow((attempt - 1) as u32);
            info!("Cycle #{} - Waiting {} seconds before retry (attempt {}/{})", 
                cycle, backoff_secs, attempt, max_attempts);
            tokio::time::sleep(Duration::from_secs(backoff_secs)).await;
        }

        match check_fe_inventory(config, client).await {
            Ok(Some(response)) => {
                let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
                
                if let Some(fe_product) = response.list_map.first() {
                    info!("[{}] Product details - SKU: {}, Active: {}, Price: {}, URL: {}", 
                        timestamp, 
                        fe_product.fe_sku,
                        fe_product.is_active,
                        fe_product.price,
                        fe_product.product_url
                    );
                    println!("[{}] 🔍 Product details:", timestamp);
                    println!("[{}]    SKU: {}", timestamp, fe_product.fe_sku);
                    println!("[{}]    Active: {}", timestamp, fe_product.is_active);
                    println!("[{}]    Price: {}", timestamp, fe_product.price);
                    println!("[{}]    URL: {}", timestamp, fe_product.product_url);
                    
                    if !fe_product.product_url.is_empty() {
                        info!("[{}] Found active product URL in FE inventory: {}", timestamp, fe_product.product_url);
                        println!("[{}] ✨ Found active product URL!", timestamp);
                        if purchase_config.enabled {
                            return launch_purchase(&fe_product.fe_sku, &fe_product.product_url).await;
                        } else {
                            println!("[{}] ⚠️ Purchase is disabled in configuration", timestamp);
                        }
                    } else {
                        info!("[{}] Product URL is empty, no product available", timestamp);
                        println!("[{}] 😴 Product URL is empty, no product available", timestamp);
                    }
                } else {
                    info!("[{}] No products found in FE inventory response", timestamp);
                    println!("[{}] 🚫 No products found in response", timestamp);
                }
                return Ok(());
            }
            Ok(None) => {
                let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
                info!("[{}] FE inventory check returned no success status", timestamp);
                println!("[{}] ❌ Server returned unsuccessful status", timestamp);
                return Ok(());
            }
            Err(e) => {
                let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
                let error_msg = format!("Error checking FE inventory: {}", e);
                warn!("[{}] {}", timestamp, error_msg);
                println!("[{}] ⚠️ {}", timestamp, error_msg);
                last_error = Some(error_msg);
                continue;
            }
        }
    }

    // If we've exhausted all retries, return the last error
    if let Some(error_msg) = last_error {
        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
        error!("[{}] Failed all {} attempts to check FE inventory", timestamp, max_attempts);
        println!("[{}] ❌ Failed all {} attempts to check FE inventory", timestamp, max_attempts);
        return Err(error_msg.into());
    }

    Ok(())
}

/// Checks the FE inventory endpoint for product availability
async fn check_fe_inventory(
    config: &ApiConfig,
    client: &reqwest::Client,
) -> Result<Option<FeInventoryResponse>, Box<dyn Error>> {
    let response = client
        .get(&config.fe_inventory_url)
        .headers(get_headers(&config.headers))
        .timeout(Duration::from_secs(config.request.timeout_secs))
        .send()
        .await?;

    // Get response text for logging
    let response_text = response.text().await?;
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    
    // Log the full response
    info!("[{}] Full server response: {}", timestamp, response_text);
    println!("[{}] 📡 Server response: {}", timestamp, response_text);

    // Parse the response
    let response: FeInventoryResponse = match serde_json::from_str(&response_text) {
        Ok(resp) => resp,
        Err(e) => {
            error!("[{}] Failed to parse response as JSON: {}", timestamp, e);
            return Err(format!("Failed to parse response as JSON: {}", e).into());
        }
    };

    if response.success {
        Ok(Some(response))
    } else {
        Ok(None)
    }
}

/// Helper function to create HeaderMap from HeadersConfig
fn get_headers(config: &HeadersConfig) -> reqwest::header::HeaderMap {
    let mut headers = reqwest::header::HeaderMap::new();
    headers.insert("User-Agent", config.user_agent.parse().unwrap());
    headers.insert("Accept", config.accept.parse().unwrap());
    headers.insert("Accept-Language", config.accept_language.parse().unwrap());
    headers.insert("Connection", config.connection.parse().unwrap());
    headers.insert("Cache-Control", config.cache_control.parse().unwrap());
    headers.insert("Pragma", config.pragma.parse().unwrap());
    headers.insert("Sec-Fetch-Dest", config.sec_fetch_dest.parse().unwrap());
    headers.insert("Sec-Fetch-Mode", config.sec_fetch_mode.parse().unwrap());
    headers.insert("Sec-Fetch-Site", config.sec_fetch_site.parse().unwrap());
    headers.insert("Origin", config.origin.parse().unwrap());
    headers.insert("Referer", config.referer.parse().unwrap());
    headers.insert("Sec-Ch-Ua", config.sec_ch_ua.parse().unwrap());
    headers.insert("Sec-Ch-Ua-Mobile", config.sec_ch_ua_mobile.parse().unwrap());
    headers.insert("Sec-Ch-Ua-Platform", config.sec_ch_ua_platform.parse().unwrap());
    headers
}

/// For testing purposes only: Simulates a product being available
pub async fn simulate_available_product(product_name: &str, purchase_config: &PurchaseConfig, force_error: bool) -> Result<(), Box<dyn Error>> {
    println!("\n[{}] 🧪 TEST MODE: Simulating product availability for '{}'", 
        Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
    
    if force_error {
        return Err("Simulated error in test mode".into());
    }
    
    if should_attempt_purchase(product_name, purchase_config) {
        launch_purchase(
            product_name,
            "https://store.nvidia.com/de-de/geforce/store/?page=1&limit=9&locale=de-de",
        ).await?;
    }
    
    Ok(())
}
