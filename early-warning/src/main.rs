use anyhow::{Context, Result};
use clap::Parser;
use log::{error, info, warn};
use notify_rust::Notification;
use reqwest::header::{HeaderMap, HeaderValue};
use rodio::{source::SineWave, OutputStream, Sink, Source};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{thread::sleep, time::{Duration, Instant}};
use chrono::Local;
use std::fs;

// Command line arguments
#[derive(Parser, Debug)]
#[command(about = "Monitor Nvidia Founders Edition inventory changes")]
struct Args {
    /// Check interval in seconds
    #[arg(short, long, default_value = "10")]
    interval: u64,

    /// Run in verbose mode
    #[arg(short, long)]
    verbose: bool,

    /// Custom endpoint URL
    #[arg(short, long, default_value = "https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=PROFESHOP5090&locale=de-de")] //PROFESHOP5090, old: Pro5090FE
    url: String,

    /// Path to reference response file
    #[arg(short, long, default_value = "config/reference_response.json")]
    reference: String,
}

// Response model
#[derive(Debug, Serialize, Deserialize, PartialEq)]
struct NvidiaResponse {
    success: bool,
    map: Option<Value>,
    #[serde(rename = "listMap")]
    list_map: Vec<ProductInfo>,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
struct ProductInfo {
    #[serde(rename = "is_active")]
    is_active: String,
    product_url: String,
    price: String,
    #[serde(rename = "fe_sku")]
    fe_sku: String,
    locale: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
struct RetailerInfo {
    sku: Option<String>,
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

    // Make request to the retailers API endpoint
    let retailers_url = "https://api.nvidia.partners/edge/product/search?page=1&limit=9&locale=de-de&category=GPU&manufacturer=NVIDIA&manufacturer_filter=NVIDIA~1";
    let retailers_response = client
        .get(retailers_url)
        .headers(headers.clone())
        .timeout(Duration::from_secs(30))
        .send()
        .await
        .context("Failed to send request to NVIDIA retailers API")?
        .json::<Value>()
        .await
        .context("Failed to parse NVIDIA retailers API response")?;

    // Check for SKU changes
    if let Some(searched_products) = retailers_response["searchedProducts"].as_object() {
        info!("Checking SKUs in retailers response...");
        if let Some(product_details) = searched_products.get("productDetails") {
            if let Some(products) = product_details.as_array() {
                for product in products {
                    if let Some(retailers) = product["retailers"].as_array() {
                        for retailer in retailers {
                            if let Some(sku) = retailer["sku"].as_str() {
                                info!("Found SKU: {}", sku);
                                // Compare with default SKUs
                                let default_skus = ["PROFESHOP5090", "PRO5080FESHOP1", "NVGFT570"];
                                if !default_skus.contains(&sku) {
                                    let msg = format!("SKU change detected! New SKU: {}", sku);
                                    warn!("{}", msg);
                                    show_notification("SKU Change Alert", &msg);
                                    play_alert_sound();
                                }
                            }
                        }
                    }
                }
            }
        }
    } else {
        info!("No searched products found in retailers response");
    }

    // Continue with the original inventory check
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

fn load_reference_response(path: &str) -> Result<NvidiaResponse> {
    let content = fs::read_to_string(path)
        .context("Failed to read reference response file")?;
    let response: NvidiaResponse = serde_json::from_str(&content)
        .context("Failed to parse reference response")?;
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

fn play_alert_sound() {
    match OutputStream::try_default() {
        Ok((_stream, stream_handle)) => {
            if let Ok(sink) = Sink::try_new(&stream_handle) {
                // Play three beeps with increasing frequency
                let frequencies = [440.0, 550.0, 660.0]; // A4, C#5, E5 notes
                
                for &freq in &frequencies {
                    let source = SineWave::new(freq)
                        .take_duration(Duration::from_millis(150))
                        .amplify(0.20);
                    
                    sink.append(source);
                    sink.sleep_until_end();
                }
            }
        }
        Err(e) => error!("Failed to play alert sound: {}", e),
    }
}

fn setup_logging(verbose: bool) -> Result<()> {
    // Create logs directory if it doesn't exist
    fs::create_dir_all("logs")?;

    // Generate log file name with timestamp
    let log_file = format!(
        "logs/nvidia-monitor_{}.log",
        Local::now().format("%Y-%m-%d_%H-%M-%S")
    );

    fern::Dispatch::new()
        // Format string for both file and console
        .format(|out, message, record| {
            out.finish(format_args!(
                "[{}] [{}] {}",
                Local::now().format("%Y-%m-%d %H:%M:%S"),
                record.level(),
                message
            ))
        })
        // Console output configuration
        .chain(fern::Dispatch::new()
            .level(if verbose { log::LevelFilter::Debug } else { log::LevelFilter::Info })
            .chain(std::io::stdout()))
        // File output configuration
        .chain(fern::Dispatch::new()
            .level(log::LevelFilter::Info)
            .chain(fern::log_file(log_file)?))
        .apply()?;

    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    // Parse command-line arguments first
    let args = Args::parse();
    
    // Initialize logging with both console and file output
    setup_logging(args.verbose)?;
    
    info!("Starting NVIDIA FE monitor...");
    info!("Monitoring URL: {}", args.url);
    info!("Check interval: {} seconds", args.interval);

    // Load reference response
    let reference_response = load_reference_response(&args.reference)?;
    info!("Loaded reference response from {}", args.reference);
    
    let mut cycle_count = 0;
    
    // Main monitoring loop
    loop {
        cycle_count += 1;
        let start_time = Instant::now();
        
        match check_nvidia_api(&args.url).await {
            Ok(response) => {
                let elapsed = start_time.elapsed();
                
                if response.success {
                    info!("API Response: {:?}", response);
                    
                    if response != reference_response {
                        warn!("Response differs from reference - possible SKU or inventory change!");
                        info!("Expected: {:?}", reference_response);
                        info!("Received: {:?}", response);
                        show_notification(
                            "NVIDIA FE Response Change!",
                            "API response differs from reference - possible SKU or inventory change!"
                        );
                        play_alert_sound();
                    } else {
                        info!(
                            "Cycle #{}: Response time: {:.2}s - Response matches reference", 
                            cycle_count,
                            elapsed.as_secs_f64()
                        );
                    }
                } else {
                    warn!(
                        "Cycle #{}: Response time: {:.2}s - Unsuccessful response", 
                        cycle_count,
                        elapsed.as_secs_f64()
                    );
                }
            }
            Err(e) => {
                let elapsed = start_time.elapsed();
                error!(
                    "Cycle #{}: Response time: {:.2}s - Error checking NVIDIA API: {}", 
                    cycle_count,
                    elapsed.as_secs_f64(),
                    e
                );
            }
        }
        
        sleep(Duration::from_secs(args.interval));
    }
}
