use anyhow::{Context, Result};
use clap::Parser;
use log::{error, info, warn};
use notify_rust::Notification;
use reqwest::header::{HeaderMap, HeaderValue};
use serde::{Deserialize, Serialize};
use std::{thread::sleep, time::Duration};

// Command line arguments
#[derive(Parser, Debug)]
#[command(about = "Monitor Nvidia Founders Edition inventory changes")]
struct Args {
    /// Check interval in seconds
    #[arg(short, long, default_value = "60")]
    interval: u64,

    /// Run in verbose mode
    #[arg(short, long)]
    verbose: bool,

    /// Custom endpoint URL
    #[arg(short, long, default_value = "https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=Pro5090FE&locale=DE")]
    url: String,
}

// Response model
#[derive(Debug, Serialize, Deserialize)]
struct NvidiaResponse {
    success: bool,
    map: Option<serde_json::Value>,
    #[serde(rename = "listMap")]
    list_map: Vec<ProductInfo>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ProductInfo {
    #[serde(rename = "is_active")]
    is_active: String,
    product_url: String,
    price: String,
    #[serde(rename = "fe_sku")]
    fe_sku: String,
    locale: String,
}

// Expected values (baseline)
struct ExpectedValues {
    is_active: String,
    product_url: String,
    fe_sku: String,
}

async fn check_nvidia_api(url: &str) -> Result<NvidiaResponse> {
    let client = reqwest::Client::new();
    
    // Configure headers based on the existing config
    let mut headers = HeaderMap::new();
    headers.insert("User-Agent", HeaderValue::from_static("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"));
    headers.insert("Accept", HeaderValue::from_static("application/json, text/plain, */*"));
    headers.insert("Accept-Language", HeaderValue::from_static("en-US,en;q=0.9,de;q=0.8"));
    headers.insert("Connection", HeaderValue::from_static("keep-alive"));
    headers.insert("Cache-Control", HeaderValue::from_static("no-cache"));
    headers.insert("Pragma", HeaderValue::from_static("no-cache"));
    headers.insert("Sec-Fetch-Dest", HeaderValue::from_static("empty"));
    headers.insert("Sec-Fetch-Mode", HeaderValue::from_static("cors"));
    headers.insert("Sec-Fetch-Site", HeaderValue::from_static("cross-site"));
    headers.insert("Origin", HeaderValue::from_static("https://www.nvidia.com"));
    headers.insert("Referer", HeaderValue::from_static("https://www.nvidia.com/"));
    headers.insert("Sec-Ch-Ua", HeaderValue::from_static("\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\""));
    headers.insert("Sec-Ch-Ua-Mobile", HeaderValue::from_static("?0"));
    headers.insert("Sec-Ch-Ua-Platform", HeaderValue::from_static("\"Windows\""));

    let response = client
        .get(url)
        .headers(headers)
        .timeout(Duration::from_secs(30))
        .send()
        .await
        .context("Failed to send request to NVIDIA API")?
        .json::<NvidiaResponse>()
        .await
        .context("Failed to parse NVIDIA API response")?;

    Ok(response)
}

fn show_notification(title: &str, body: &str) {
    if let Err(e) = Notification::new()
        .summary(title)
        .body(body)
        .timeout(0) // Never timeout
        .show() {
        error!("Failed to show notification: {}", e);
    }
}

fn detect_changes(expected: &ExpectedValues, actual: &ProductInfo, verbose: bool) -> bool {
    let mut changed = false;
    let mut changes = Vec::new();

    if expected.is_active != actual.is_active {
        changes.push(format!(
            "is_active changed: '{}' -> '{}'",
            expected.is_active, actual.is_active
        ));
        changed = true;
    }

    if expected.product_url != actual.product_url {
        changes.push(format!(
            "product_url changed: '{}' -> '{}'",
            expected.product_url, actual.product_url
        ));
        changed = true;
    }

    if expected.fe_sku != actual.fe_sku {
        changes.push(format!(
            "fe_sku changed: '{}' -> '{}'",
            expected.fe_sku, actual.fe_sku
        ));
        changed = true;
    }

    if changed {
        let change_message = changes.join("\n");
        warn!("Detected changes: \n{}", change_message);
        show_notification(
            "NVIDIA FE Status Change Detected!",
            &format!("Changes detected in the Founders Edition status:\n{}", change_message),
        );
    } else if verbose {
        info!("No changes detected. Values remain the same.");
    }

    changed
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize the logger
    env_logger::init();
    
    // Parse command-line arguments
    let args = Args::parse();
    
    // Set up expected values (baseline)
    let expected = ExpectedValues {
        is_active: "false".to_string(),
        product_url: "".to_string(),
        fe_sku: "Pro5090FE_DE".to_string(),
    };

    info!("Starting NVIDIA FE monitor...");
    info!("Monitoring URL: {}", args.url);
    info!("Check interval: {} seconds", args.interval);
    
    // Main monitoring loop
    loop {
        match check_nvidia_api(&args.url).await {
            Ok(response) => {
                if args.verbose {
                    info!("Received response: {:?}", response);
                }
                
                if response.success && !response.list_map.is_empty() {
                    let product = &response.list_map[0];
                    detect_changes(&expected, product, args.verbose);
                } else {
                    warn!("Received unexpected response format or empty list");
                    if args.verbose {
                        info!("Response: {:?}", response);
                    }
                }
            }
            Err(e) => {
                error!("Error checking NVIDIA API: {}", e);
            }
        }

        // Wait for the specified interval before checking again
        sleep(Duration::from_secs(args.interval));
    }
}
