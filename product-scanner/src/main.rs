use std::error::Error;
use std::time::Duration;
use config::{Config, File};
use serde::Deserialize;

/// Configuration struct to deserialize from the config file
#[derive(Debug, Deserialize)]
struct AppConfig {
    url: String,
    request: RequestConfig,
    headers: HeadersConfig,
}

#[derive(Debug, Deserialize)]
struct RequestConfig {
    timeout_secs: u64,
    connect_timeout_secs: u64,
    max_attempts: u32,
}

#[derive(Debug, Deserialize)]
struct HeadersConfig {
    user_agent: String,
    accept: String,
    accept_language: String,
    connection: String,
    cache_control: String,
    pragma: String,
    sec_fetch_dest: String,
    sec_fetch_mode: String,
    sec_fetch_site: String,
    origin: String,
    referer: String,
    sec_ch_ua: String,
    sec_ch_ua_mobile: String,
    sec_ch_ua_platform: String,
}

/// Loads configuration from config files
fn load_config() -> Result<AppConfig, config::ConfigError> {
    let config = Config::builder()
        .add_source(File::with_name("config/default"))
        .build()?;
    
    config.try_deserialize()
}

/// Makes a request to NVIDIA API and logs the response with retry capability
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Load configuration
    let config = load_config()?;
    println!("Configuration loaded successfully");
    
    println!("Attempting to access NVIDIA API...");
    
    // Create a client with better browser emulation
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(config.request.timeout_secs))
        .connect_timeout(Duration::from_secs(config.request.connect_timeout_secs))
        .danger_accept_invalid_certs(true)  // Try accepting invalid certs
        .user_agent(&config.headers.user_agent)
        .build()?;
    
    // Maximum number of attempts
    let max_attempts = config.request.max_attempts;
    let mut last_error = None;
    
    // Try the request with retries
    for attempt in 1..=max_attempts {
        println!("\nAttempt {}/{}", attempt, max_attempts);
        
        // Calculate backoff time (exponential backoff)
        if attempt > 1 {
            let backoff_secs = 2_u64.pow((attempt - 1) as u32);
            println!("Waiting {} seconds before retry...", backoff_secs);
            tokio::time::sleep(Duration::from_secs(backoff_secs)).await;
        }
        
        // Build request with detailed headers that look more like a real browser
        println!("Sending request with common browser headers...");
        let request = client.get(&config.url)
            .header("Accept", &config.headers.accept)
            .header("Accept-Language", &config.headers.accept_language)
            // Don't specify Accept-Encoding to let reqwest handle it
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
        let response_result = request.send().await;
            
        match response_result {
            Ok(response) => {
                // Log response info
                println!("Response status: {}", response.status());
                println!("Response headers:");
                for (name, value) in response.headers() {
                    if let Ok(v) = value.to_str() {
                        println!("  {}: {}", name, v);
                    }
                }
                
                // Check if successful
                if response.status().is_success() {
                    // Get response bytes instead of text for binary data
                    match response.bytes().await {
                        Ok(bytes) => {
                            println!("Successfully received response with length: {} bytes", bytes.len());

                            // Parse as JSON, printing the result if successful
                            match serde_json::from_slice::<serde_json::Value>(&bytes) {
                                Ok(json) => {
                                    let formatted_json = serde_json::to_string_pretty(&json)?;
                                    println!("Response from NVIDIA API:\n{}", formatted_json);
                                    return Ok(());
                                },
                                Err(e) => {
                                    println!("Couldn't parse response as JSON: {}", e);                                   
                                }
                            }
                        },
                        Err(e) => {
                            println!("Error reading response body: {}", e);
                            last_error = Some(format!("Error reading response body: {}", e));
                        }
                    }
                } else {
                    let status = response.status();
                    match response.bytes().await {
                        Ok(bytes) => {
                            println!("Error response length: {} bytes", bytes.len());
                            println!("First 100 bytes: {:?}", &bytes.iter().take(100).collect::<Vec<_>>());
                        }
                        Err(e) => println!("Could not read error response: {}", e)
                    }
                    
                    last_error = Some(format!("HTTP error status: {}", status));
                }
            },
            Err(e) => {
                println!("Request failed: {}", e);
                println!("Error details: {:?}", e);
                last_error = Some(format!("Request error: {}", e));
            }
        }
    }
    
    // If we get here, all attempts failed
    let error_msg = last_error.unwrap_or_else(|| "All requests failed with unknown errors".to_string());
    println!("\nAll {} request attempts failed. Last error: {}", max_attempts, error_msg);
    Err(error_msg.into())
}
