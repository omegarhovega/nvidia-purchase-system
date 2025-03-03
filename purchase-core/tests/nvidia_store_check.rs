use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    // Target URL - using the original store URL
    let url = "https://store.nvidia.com/de-de/geforce/store";
    
    println!("[INFO] Sending request to {}", url);
    
    // Create a request with headers
    let response = attohttpc::get(url)
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        .header("sec-fetch-dest", "document")
        .header("sec-fetch-mode", "navigate")
        .header("sec-fetch-site", "none")
        .timeout(std::time::Duration::from_secs(30))
        .follow_redirects(true)
        .send()?;
    
    // Print response details
    println!("[INFO] Status Code: {}", response.status());
    println!("[INFO] Final URL: {}", response.url());
    
    // Print response headers
    println!("\n[INFO] Response Headers:");
    for (name, value) in response.headers() {
        println!("  {}: {}", name, value.to_str().unwrap_or("Invalid UTF-8"));
    }
    
    // Get the response body
    let text = response.text()?;
    println!("[INFO] Response: {} bytes", text.len());
    
    Ok(())
}