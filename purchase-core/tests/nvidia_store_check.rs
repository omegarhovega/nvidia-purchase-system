use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    // Target URL - using the original store URL
    let url = "https://store.nvidia.com/de-de/geforce/store";
    
    println!("[INFO] Sending request to {}", url);
    
    // Manually track redirects
    let mut redirect_history = Vec::new();
    let mut current_url = url.to_string();
    let mut response = None;
    
    // Maximum number of redirects to follow
    let max_redirects = 10;
    let mut redirect_count = 0;
    
    while redirect_count < max_redirects {
        // Make the request without following redirects
        let resp = attohttpc::get(&current_url)
            .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            .header("sec-fetch-dest", "document")
            .header("sec-fetch-mode", "navigate")
            .header("sec-fetch-site", "none")
            .timeout(std::time::Duration::from_secs(30))
            .follow_redirects(false) // Don't automatically follow redirects
            .send()?;
        
        let status = resp.status();
        
        // If it's a redirect, follow it
        if status.is_redirection() {
            // Add to redirect history
            redirect_history.push((status, current_url.clone()));
            
            // Get the Location header
            if let Some(location) = resp.headers().get("location") {
                let location_str = location.to_str().unwrap_or("");
                
                // Handle relative URLs
                current_url = if location_str.starts_with("http") {
                    location_str.to_string()
                } else {
                    // Simple relative URL handling
                    let base_url = current_url.split('/').take(3).collect::<Vec<_>>().join("/");
                    if location_str.starts_with('/') {
                        format!("{}{}", base_url, location_str)
                    } else {
                        format!("{}/{}", base_url, location_str)
                    }
                };
                
                redirect_count += 1;
            } else {
                // No Location header in redirect
                return Err("Redirect without Location header".into());
            }
        } else {
            // Not a redirect, we're done
            response = Some(resp);
            break;
        }
    }
    
    // Get the final response
    let final_response = match response {
        Some(r) => r,
        None => return Err("Too many redirects".into()),
    };
    
    // Print response details
    println!("[INFO] Status Code: {}", final_response.status());
    println!("[INFO] Final URL: {}", current_url);
    
    // Print response headers
    println!("\n[INFO] Response Headers:");
    for (name, value) in final_response.headers() {
        println!("  {}: {}", name, value.to_str().unwrap_or("Invalid UTF-8"));
    }
    
    // Print redirect history
    if !redirect_history.is_empty() {
        println!("\n[INFO] Redirect History:");
        for (i, (status, url)) in redirect_history.iter().enumerate() {
            println!("  Redirect {}: {} - {}", i+1, status, url);
        }
    } else {
        println!("\n[INFO] No redirects occurred");
    }
    
    // Get the response body
    let text = final_response.text()?;
    println!("[INFO] Response: {} bytes", text.len());
    
    Ok(())
}