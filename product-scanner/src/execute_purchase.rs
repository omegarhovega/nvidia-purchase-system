use std::error::Error;
use std::fs::{self, File};
use std::io::Write;
use std::time::Instant;
use serde::{Deserialize, Serialize};
use serde_json::{self, json};
use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;
use chrono::Local;

#[derive(Debug, Serialize, Deserialize)]
struct Cookie {
    name: String,
    value: String,
    domain: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct CookieData {
    cookies: Vec<Cookie>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Redirect {
    from: String,
    to: String,
    status_code: u16,
}

#[derive(Debug, Serialize, Deserialize)]
struct RedirectHistory {
    timestamp: String,
    final_url: String,
    redirects: Vec<Redirect>,
}

fn get_shared_scripts_path() -> std::path::PathBuf {
    let current_dir = std::env::current_dir().expect("Failed to get current directory");
    let root_dir = current_dir
        .parent()
        .expect("Failed to get parent directory");
    root_dir.join("shared").join("scripts")
}

fn get_timestamp() -> String {
    let now = Local::now();
    // Format timestamp without colons for filename safety
    now.format("%Y-%m-%d_%H-%M-%S").to_string()
}

fn generate_unique_filename() -> String {
    let random_string: String = thread_rng()
        .sample_iter(&Alphanumeric)
        .take(8)
        .map(char::from)
        .collect();
    format!("captured_purchase_cookies_{}_{}.json", get_timestamp(), random_string)
}

pub fn fast_purchase(purchase_url: &str) -> Result<bool, Box<dyn Error>> {
    // Start timing
    let start_time = Instant::now();

    // Load cookies from file
    let cookies_path = get_shared_scripts_path().join("captured_cookies.json");
    println!("[INFO] Loading cookies from {}", cookies_path.display());
    
    let cookie_file = fs::read_to_string(&cookies_path)?;
    let cookie_data: CookieData = serde_json::from_str(&cookie_file)?;
    
    println!("[INFO] Loaded {} cookies from {}", cookie_data.cookies.len(), cookies_path.display());

    // Check for CloudFlare clearance cookie
    let cf_clearance = cookie_data.cookies.iter()
        .find(|cookie| cookie.name == "cf_clearance")
        .map(|cookie| &cookie.value);
    
    if let Some(clearance) = cf_clearance {
        let preview = if clearance.len() > 10 {
            format!("{}...", &clearance[..10])
        } else {
            clearance.clone()
        };
        println!("[INFO] Found cf_clearance cookie: {}", preview);
    } else {
        println!("[ERROR] No Cloudflare clearance cookie found");
        return Ok(false);
    }

    // Create request with cookies
    let mut request = attohttpc::get(purchase_url);
    
    // Add cookies to the request - using a single Cookie header with all cookies
    let mut all_cookies = String::new();
    for cookie in &cookie_data.cookies {
        if !all_cookies.is_empty() {
            all_cookies.push_str("; ");
        }
        all_cookies.push_str(&format!("{}={}", cookie.name, cookie.value));
    }
    
    // Add the combined cookie header
    request = request.header("Cookie", all_cookies);

    // Set browser fingerprinting headers - MUST match original request to obtain cf_clearance cookie
    request = request
        .header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8")
        .header("Accept-Language", "de-DE,de;q=0.7")
        .header("priority", "u=0, i")
        .header("referer", "https://marketplace.nvidia.com/")
        .header("sec-ch-ua", "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"")
        .header("sec-ch-ua-arch", "\"x86\"")
        .header("sec-ch-ua-bitness", "\"64\"")
        .header("sec-ch-ua-full-version-list", "\"Chromium\";v=\"134.0.0.0\", \"Not:A-Brand\";v=\"24.0.0.0\", \"Brave\";v=\"134.0.0.0\"")
        .header("sec-ch-ua-mobile", "?0")
        .header("sec-ch-ua-model", "\"\"")
        .header("sec-ch-ua-platform", "\"Windows\"")
        .header("sec-ch-ua-platform-version", "\"19.0.0\"")
        .header("sec-fetch-dest", "document")
        .header("sec-fetch-mode", "navigate")
        .header("sec-fetch-site", "cross-site")
        .header("sec-fetch-user", "?1")
        .header("sec-gpc", "1")
        .header("upgrade-insecure-requests", "1")
        .header("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36");

    println!("[INFO] Making request to {}", purchase_url);

    // Make request with automatic redirect handling and increased timeout
    let response = request
        .timeout(std::time::Duration::from_secs(60))  // Increased timeout to match Python
        .follow_redirects(true)
        .send()?;

    // Store important information before consuming the response
    let status = response.status();
    let final_url = response.url().to_string();
    
    // Extract cookies from response headers
    let mut updated_cookies = Vec::new();
    
    // Process Set-Cookie headers if present
    for header in response.headers().iter() {
        if header.0.as_str().to_lowercase() == "set-cookie" {
            if let Ok(cookie_str) = header.1.to_str() {
                // More comprehensive cookie parsing
                let parts: Vec<&str> = cookie_str.split(';').collect();
                if let Some(name_value) = parts.first() {
                    if let Some((name, value)) = name_value.split_once('=') {
                        // Try to extract domain from cookie string
                        let domain = parts.iter()
                            .find(|part| part.trim().to_lowercase().starts_with("domain="))
                            .and_then(|domain_part| domain_part.split_once('='))
                            .map(|(_, domain)| domain.trim().to_string());
                        
                        updated_cookies.push(Cookie {
                            name: name.trim().to_string(),
                            value: value.trim().to_string(),
                            domain,
                        });
                    }
                }
            }
        }
    }
    
    // Print the final URL after all redirects
    println!("[INFO] Final URL after redirects: {}", final_url);

    // Get response body - this consumes the response
    let response_text = response.text()?;

    // Save the final HTML page
    let html_output_path = get_shared_scripts_path().join("final_page_rs.html");
    let mut file = File::create(&html_output_path)?;
    file.write_all(response_text.as_bytes())?;
    println!("[INFO] Saved final page HTML to {}", html_output_path.display());

    // Unfortunately, attohttpc doesn't provide redirect history directly
    // We'll just create an empty history for now
    let redirect_history = RedirectHistory {
        timestamp: get_timestamp(),
        final_url,
        redirects: Vec::new(),
    };

    // Save redirect history
    let redirects_output_path = get_shared_scripts_path().join("redirect_history_rs.json");
    let redirect_json = serde_json::to_string_pretty(&redirect_history)?;
    let mut file = File::create(&redirects_output_path)?;
    file.write_all(redirect_json.as_bytes())?;
    println!("[INFO] Saved redirect history to {}", redirects_output_path.display());

    // Combine original cookies with any new ones
    for cookie in cookie_data.cookies {
        if !updated_cookies.iter().any(|c| c.name == cookie.name) {
            updated_cookies.push(cookie);
        }
    }

    // Save updated cookies
    let output_data = json!({
        "timestamp": get_timestamp(),
        "cookies": updated_cookies
    });

    let filename = generate_unique_filename();
    let cookies_output_path = get_shared_scripts_path().join(filename);
    let cookie_json = serde_json::to_string_pretty(&output_data)?;
    let mut file = File::create(&cookies_output_path)?;
    file.write_all(cookie_json.as_bytes())?;
    println!("[INFO] Saved cookies to {}", cookies_output_path.display());

    // Check for ASP.NET_SessionId cookie
    let asp_session = updated_cookies.iter()
        .find(|cookie| cookie.name == "ASP.NET_SessionId")
        .map(|cookie| &cookie.value);
    
    if let Some(session) = asp_session {
        println!("[INFO] Found ASP.NET_SessionId cookie: {}", session);
    } else {
        println!("[WARNING] No ASP.NET_SessionId cookie found");
    }

    // Report results
    let elapsed_time = start_time.elapsed();
    println!(
        "[INFO] Request completed with status {} in {:.2}s",
        status,
        elapsed_time.as_secs_f64()
    );

    Ok(status.is_success())
}

// For testing purposes only to run script standalone
#[allow(dead_code)]
pub fn main() -> Result<(), Box<dyn Error>> {
    // Default test URL
    let default_url = "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D";

    // Run the purchase function
    match fast_purchase(default_url) {
        Ok(true) => println!("[INFO] Purchase attempt completed successfully!"),
        Ok(false) => println!("[ERROR] Purchase attempt failed"),
        Err(e) => println!("[ERROR] Purchase attempt failed with error: {}", e),
    }

    Ok(())
}
