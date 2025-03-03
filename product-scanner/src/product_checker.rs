use std::error::Error;
use std::time::{Duration, Instant};
use serde_json::Value;
use chrono::Local;
use log::{info, warn, error};
use reqwest;

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
    pub rtx_5080: String,
    pub rtx_5090: String,
}

pub struct RequestConfig {
    pub timeout_secs: u64,
    pub connect_timeout_secs: u64,
    pub max_attempts: u32,
}

/// Makes a request to NVIDIA API and checks product availability
pub async fn check_nvidia_api(
    config: &ApiConfig, 
    client: &reqwest::Client,
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
            
        match response_result {
            Ok(response) => {
                let status = response.status();
                info!("Cycle #{} - Response status: {}, Time: {}ms", cycle, status, response_time);
                
                // Check if successful
                if status.is_success() {
                    // Get response bytes
                    match response.bytes().await {
                        Ok(bytes) => {
                            let response_length = bytes.len();
                            info!("Cycle #{} - Successfully received response with length: {} bytes", cycle, response_length);
                            
                            // Parse as JSON
                            match serde_json::from_slice::<serde_json::Value>(&bytes) {
                                Ok(json) => {
                                    let mut product_statuses = Vec::new();
                                    
                                    if let Some(searched_products) = json["searchedProducts"].as_object() {
                                        if let Some(product_details) = searched_products.get("productDetails") {
                                            if let Some(products) = product_details.as_array() {
                                                if products.is_empty() {
                                                    let msg = "No products found in the API response.";
                                                    warn!("Cycle #{} - {}", cycle, msg);
                                                    println!("[{}] Cycle #{} - {}", 
                                                             Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                                                } else {
                                                    for product in products {
                                                        let (name, available) = check_product_availability(
                                                            product, 
                                                            &config.default_links.rtx_5080,
                                                            &config.default_links.rtx_5090
                                                        );
                                                        let status = if available { "AVAILABLE" } else { "NOT AVAILABLE" };
                                                        product_statuses.push((name, status.to_string()));
                                                    }
                                                }
                                            } else {
                                                let msg = "productDetails is not an array";
                                                warn!("Cycle #{} - {}", cycle, msg);
                                                println!("[{}] Cycle #{} - {}", 
                                                         Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                                            }
                                        } else {
                                            let msg = "productDetails not found in the response";
                                            warn!("Cycle #{} - {}", cycle, msg);
                                            println!("[{}] Cycle #{} - {}", 
                                                     Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                                        }
                                    } else {
                                        let msg = "searchedProducts not found in the response";
                                        warn!("Cycle #{} - {}", cycle, msg);
                                        println!("[{}] Cycle #{} - {}", 
                                                 Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
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
                                },
                                Err(e) => {
                                    let msg = format!("Couldn't parse response as JSON: {}", e);
                                    error!("Cycle #{} - {}", cycle, msg);
                                    println!("[{}] Cycle #{} - {}", 
                                             Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                                    last_error = Some(msg);
                                }
                            }
                        },
                        Err(e) => {
                            let msg = format!("Error reading response body: {}", e);
                            error!("Cycle #{} - {}", cycle, msg);
                            println!("[{}] Cycle #{} - {}", 
                                     Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                            last_error = Some(msg);
                        }
                    }
                } else {
                    let msg = format!("HTTP error status: {} ({})", status, status.canonical_reason().unwrap_or("Unknown"));
                    error!("Cycle #{} - {}", cycle, msg);
                    println!("[{}] Cycle #{} - {}", 
                             Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                    last_error = Some(msg);
                }
            },
            Err(e) => {
                let msg = format!("Request error: {}", e);
                error!("Cycle #{} - {}", cycle, msg);
                println!("[{}] Cycle #{} - {}", 
                         Local::now().format("%Y-%m-%d %H:%M:%S"), cycle, msg);
                last_error = Some(msg);
            }
        }
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
