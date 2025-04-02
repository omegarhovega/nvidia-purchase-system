use std::error::Error;
use std::time::Duration;
use chrono::Local;
use log::{info, warn};
use reqwest;
use serde::{Deserialize, Serialize};

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

/// Checks the FE inventory endpoint for product availability
async fn check_fe_inventory(
    config: &ApiConfig,
    client: &reqwest::Client,
) -> Result<String, Box<dyn Error>> {
    // Add timestamp for cache busting
    let timestamp = chrono::Utc::now().timestamp_millis();
    let url = if config.fe_inventory_url.contains('?') {
        format!("{}&t={}", config.fe_inventory_url, timestamp)
    } else {
        format!("{}?t={}", config.fe_inventory_url, timestamp)
    };
    
    let response = client
        .get(&url)
        .headers(get_headers(&config.headers))
        .timeout(Duration::from_secs(config.request.timeout_secs))
        .send()
        .await?;

    // Get response text for logging
    let response_text = response.text().await?;
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    
    // Log the full response
    info!("[{}] Server response: {}", timestamp, &response_text);
    println!("[{}] 📡 Server response: {}", timestamp, &response_text);

    Ok(response_text)
}

/// Makes a request to NVIDIA FE inventory API and checks product availability
/// Returns the product URL if a product is available, otherwise None
pub async fn check_nvidia_api(
    config: &ApiConfig, 
    _client: &reqwest::Client, 
    cycle: u64
) -> Result<Option<(String, String)>, Box<dyn Error>> {
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

        // Create a new client for each attempt
        let new_client = reqwest::Client::builder()
            .timeout(Duration::from_secs(config.request.timeout_secs))
            .user_agent(&config.headers.user_agent)
            .build()?;

        match check_fe_inventory(config, &new_client).await {
            Ok(response_text) => {
                // Only parse and check for purchase if needed
                match serde_json::from_str::<FeInventoryResponse>(&response_text) {
                    Ok(parsed) if parsed.success => {
                        // Check for products with URLs
                        let available_product = parsed.list_map.iter()
                            .find(|product| !product.product_url.is_empty());
                        
                        if let Some(product) = available_product {
                            // Return product information instead of launching purchase
                            let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
                            println!("[{}] 🔍 Found available product: {}", timestamp, product.fe_sku);
                            return Ok(Some((product.fe_sku.clone(), product.product_url.clone())));
                        } else {
                            // No URL found
                            let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
                            println!("[{}] ❌ No product URL found", timestamp);
                        }
                    },
                    _ => {
                        // Failed to parse or unsuccessful response
                        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
                        println!("[{}] ❌ No product URL found", timestamp);
                    }
                }
                return Ok(None);
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
    
    // If we've exhausted all attempts, return the last error
    if let Some(error_msg) = last_error {
        Err(error_msg.into())
    } else {
        Err("Failed to check FE inventory after all attempts".into())
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
pub async fn simulate_available_product(product_name: &str, force_error: bool) -> Result<Option<(String, String)>, Box<dyn Error>> {
    println!("\n[{}] 🧪 TEST MODE: Simulating product availability for '{}'", 
        Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
    
    if force_error {
        return Err("Simulated error in test mode".into());
    }
    
    // Use the sample URL for testing
    let sample_url = "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=bFHncOsrkXFbYRF56H68bUYIDb5AcZcdMLlBR44dZW46fqwfc5XdgVX7GcBoTv0MPqdirRx3xR%2B%2BHzx%2BBotzaO%2F4L%2FlTqKPHplY5e9vGhWSXFRzoebTbYEhykPPVXJ4u2DB0yTMDccuO1cXeoNsy2MRNf3G9p3fUSVp9zASLJ0uJymzkdEijj0QKsZLS8I4GQ252Y7yAUFDboHiEt9TDvJ3Fo1HXw9KXeueIUZ432lQhBuzhHR78O9N%2FbJldC6r9YdeRgCszPH2m2u7VRaaZPasTuvylSd0yj7tOxQOTou85%2BV7D%2Fw3brZng%2Bc5t4CE6vL0qKGsyvL4lH%2FfCE3YWkQ%3D%3D";
    
    println!("[{}] 🔗 Found sample URL for testing: {}", 
        Local::now().format("%Y-%m-%d %H:%M:%S"), sample_url);
    
    // Return the product information instead of launching purchase
    Ok(Some((product_name.to_string(), sample_url.to_string())))
}
