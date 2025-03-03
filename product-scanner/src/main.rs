use std::error::Error;
use std::time::Duration;
use std::fs::File;
use std::io::Write;

/// Makes a request to NVIDIA API and logs the response with retry capability
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Define the API URL
    let url = "https://api.nvidia.partners/edge/product/search?page=1&limit=9&manufacturer_filter=NVIDIA%7E1&category=GPU&locale=de-de&manufacturer=NVIDIA";
    
    println!("Attempting to access NVIDIA API...");
    
    // Create a client with better browser emulation
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(30))  // Use a longer timeout
        .connect_timeout(Duration::from_secs(15))
        .danger_accept_invalid_certs(true)  // Try accepting invalid certs
        .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        .build()?;
    
    // Maximum number of attempts
    let max_attempts = 4;
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
        let request = client.get(url)
            .header("Accept", "application/json, text/plain, */*")
            .header("Accept-Language", "en-US,en;q=0.9,de;q=0.8")
            // Don't specify Accept-Encoding to let reqwest handle it
            .header("Connection", "keep-alive")
            .header("Cache-Control", "no-cache")
            .header("Pragma", "no-cache")
            .header("Sec-Fetch-Dest", "empty")
            .header("Sec-Fetch-Mode", "cors")
            .header("Sec-Fetch-Site", "cross-site")
            .header("Origin", "https://www.nvidia.com")
            .header("Referer", "https://www.nvidia.com/")
            .header("sec-ch-ua", "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\"")
            .header("sec-ch-ua-mobile", "?0")
            .header("sec-ch-ua-platform", "\"Windows\"");
        
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
                            
                            // Save the raw response to a file for examination
                            let filename = format!("nvidia_response_attempt_{}.bin", attempt);
                            match File::create(&filename) {
                                Ok(mut file) => {
                                    if let Err(e) = file.write_all(&bytes) {
                                        println!("Failed to write response to file: {}", e);
                                    } else {
                                        println!("Raw response saved to {}", filename);
                                    }
                                },
                                Err(e) => println!("Failed to create file: {}", e),
                            }
                            
                            // Try to parse as JSON anyway, printing the result if successful
                            match serde_json::from_slice::<serde_json::Value>(&bytes) {
                                Ok(json) => {
                                    let formatted_json = serde_json::to_string_pretty(&json)?;
                                    println!("Response from NVIDIA API:\n{}", formatted_json);
                                    return Ok(());
                                },
                                Err(e) => {
                                    println!("Couldn't parse response as JSON: {}", e);
                                    
                                    // Try to convert to string and print first part
                                    match std::str::from_utf8(&bytes) {
                                        Ok(text) => {
                                            println!("First 200 chars as UTF-8: {}", 
                                                &text.chars().take(200).collect::<String>());
                                        },
                                        Err(_) => {
                                            println!("Response is not valid UTF-8 text");
                                            // Print first few bytes as hex
                                            let max_bytes = std::cmp::min(bytes.len(), 50);
                                            let hex_bytes: Vec<String> = bytes.iter()
                                                .take(max_bytes)
                                                .map(|b| format!("{:02X}", b))
                                                .collect();
                                            println!("First {} bytes (hex): {}", max_bytes, hex_bytes.join(" "));
                                        }
                                    }
                                    
                                    println!("Request succeeded but response format isn't standard JSON");
                                    return Ok(());
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
