use std::error::Error;
use std::time::Duration;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use rand::Rng;
use chrono::Local;
use log::{info, error};
use reqwest;
use config::Config as AppConfig;
use tokio;
use std::env;
use std::time::Instant;

mod product_checker;
mod execute_purchase;

use product_checker::{check_nvidia_api, ApiConfig, HeadersConfig, RequestConfig, simulate_available_product};
use execute_purchase::fast_purchase;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Check for test mode
    let args: Vec<String> = env::args().collect();
    let test_mode = args.len() > 1 && (args[1] == "--test" || args[1] == "--test-error");
    let test_error_mode = args.len() > 1 && args[1] == "--test-error";
    
    // Load configuration
    let settings = AppConfig::builder()
        .add_source(config::File::with_name("config/default"))
        .build()?;
    
    // Extract configuration values
    let fe_inventory_url = settings.get_string("fe_inventory_url")?;
    let timeout_secs = settings.get_int("request.timeout_secs")? as u64;
    let max_attempts = settings.get_int("request.max_attempts")? as u32;
    let sleep_ms_min = settings.get_int("request.sleep_ms_min")? as u64;
    let sleep_ms_max = settings.get_int("request.sleep_ms_max")? as u64;

    // Extract headers
    let user_agent = settings.get_string("headers.user_agent")?;
    let accept = settings.get_string("headers.accept")?;
    let accept_language = settings.get_string("headers.accept_language")?;
    let connection = settings.get_string("headers.connection")?;
    let cache_control = settings.get_string("headers.cache_control")?;
    let pragma = settings.get_string("headers.pragma")?;
    let sec_fetch_dest = settings.get_string("headers.sec_fetch_dest")?;
    let sec_fetch_mode = settings.get_string("headers.sec_fetch_mode")?;
    let sec_fetch_site = settings.get_string("headers.sec_fetch_site")?;
    let origin = settings.get_string("headers.origin")?;
    let referer = settings.get_string("headers.referer")?;
    let sec_ch_ua = settings.get_string("headers.sec_ch_ua")?;
    let sec_ch_ua_mobile = settings.get_string("headers.sec_ch_ua_mobile")?;
    let sec_ch_ua_platform = settings.get_string("headers.sec_ch_ua_platform")?;
    
    // Create API configuration
    let api_config = ApiConfig {
        fe_inventory_url,
        headers: HeadersConfig {
            user_agent,
            accept,
            accept_language,
            connection,
            cache_control,
            pragma,
            sec_fetch_dest,
            sec_fetch_mode,
            sec_fetch_site,
            origin,
            referer,
            sec_ch_ua,
            sec_ch_ua_mobile,
            sec_ch_ua_platform,
        },
        request: RequestConfig {
            timeout_secs,
            max_attempts,
            sleep_ms_min,
            sleep_ms_max,
        },
    };
    
    // Create a dummy client just for compatibility - we'll create new ones for each request
    let client = reqwest::Client::new();
    
    println!("[{}] Configuration loaded successfully", Local::now().format("%Y-%m-%d %H:%M:%S"));
    info!("Configuration loaded successfully");
    
    // If in test mode, run the test and exit
    if test_mode {
        println!("[{}] Running in TEST MODE{}", 
                Local::now().format("%Y-%m-%d %H:%M:%S"),
                if test_error_mode { " (with forced error)" } else { "" });
        info!("Running in TEST MODE{}", if test_error_mode { " (with forced error)" } else { "" });
        
        // Test with RTX 5090
        match simulate_available_product("GeForce RTX 5090", test_error_mode).await {
            Ok(Some((product_name, product_url))) => {
                println!("[{}] 🚀 TEST MODE: Initiating purchase for {}", 
                         Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
                
                // Measure purchase execution time
                let start_time = Instant::now();
                
                match fast_purchase(&product_url) {
                    Ok(true) => {
                        let elapsed = start_time.elapsed();
                        println!("[{}] ✅ TEST MODE: Purchase completed successfully in {:.2}s", 
                                 Local::now().format("%Y-%m-%d %H:%M:%S"), elapsed.as_secs_f64());
                    },
                    Ok(false) => {
                        let elapsed = start_time.elapsed();
                        println!("[{}] ⚠️ TEST MODE: Purchase attempt failed in {:.2}s", 
                                 Local::now().format("%Y-%m-%d %H:%M:%S"), elapsed.as_secs_f64());
                    },
                    Err(e) => {
                        let elapsed = start_time.elapsed();
                        println!("[{}] ❌ TEST MODE: Purchase attempt failed with error in {:.2}s: {}", 
                                 Local::now().format("%Y-%m-%d %H:%M:%S"), elapsed.as_secs_f64(), e);
                    }
                }
            },
            Ok(None) => {
                println!("[{}] ⚠️ TEST MODE: No product URL found in simulation", 
                         Local::now().format("%Y-%m-%d %H:%M:%S"));
            },
            Err(e) => {
                error!("Failed to simulate product availability: {}", e);
                println!("[{}] ❌ TEST MODE: Failed to simulate product availability: {}", 
                         Local::now().format("%Y-%m-%d %H:%M:%S"), e);
            }
        }
        
        println!("[{}] Test completed, exiting", Local::now().format("%Y-%m-%d %H:%M:%S"));
        info!("Test completed, exiting");
        return Ok(());
    }
    
    // Set up Ctrl+C handler
    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();
    
    ctrlc::set_handler(move || {
        println!("\n[{}] Received Ctrl+C, shutting down...", Local::now().format("%Y-%m-%d %H:%M:%S"));
        info!("Received Ctrl+C, shutting down...");
        r.store(false, Ordering::SeqCst);
    })?;
    
    println!("[{}] Starting continuous product availability check (Press Ctrl+C to exit)", 
             Local::now().format("%Y-%m-%d %H:%M:%S"));
    info!("Starting continuous product availability check");
    
    // Main loop
    let mut cycle: u64 = 0;
    let mut rng = rand::thread_rng();
    
    while running.load(Ordering::SeqCst) {
        cycle += 1;
        
        // Check NVIDIA API for available products
        match check_nvidia_api(&api_config, &client, cycle).await {
            Ok(Some((product_name, product_url))) => {
                // Product is available, initiate purchase immediately
                println!("[{}] 🚀 LAUNCHING PURCHASE PROCESS FOR: {}", 
                         Local::now().format("%Y-%m-%d %H:%M:%S"), product_name);
                println!("[{}] 🔗 Product Link: {}", 
                         Local::now().format("%Y-%m-%d %H:%M:%S"), product_url);
                
                // Measure purchase execution time
                let start_time = Instant::now();
                
                // Execute the purchase directly
                match fast_purchase(&product_url) {
                    Ok(true) => {
                        let elapsed = start_time.elapsed();
                        println!("[{}] ✅ Purchase process completed successfully in {:.2}s", 
                                 Local::now().format("%Y-%m-%d %H:%M:%S"), elapsed.as_secs_f64());
                    },
                    Ok(false) => {
                        let elapsed = start_time.elapsed();
                        println!("[{}] ⚠️ Purchase attempt failed in {:.2}s", 
                                 Local::now().format("%Y-%m-%d %H:%M:%S"), elapsed.as_secs_f64());
                    },
                    Err(e) => {
                        let elapsed = start_time.elapsed();
                        println!("[{}] ❌ Purchase attempt failed with error in {:.2}s: {}", 
                                 Local::now().format("%Y-%m-%d %H:%M:%S"), elapsed.as_secs_f64(), e);
                    }
                }
            },
            Ok(None) => {
                // No product available, continue monitoring
            },
            Err(e) => {
                error!("Cycle #{} - Failed to check NVIDIA API: {}", cycle, e);
            }
        }
        
        // Random sleep between configured min and max values
        if running.load(Ordering::SeqCst) {
            let sleep_ms = rng.gen_range(api_config.request.sleep_ms_min..api_config.request.sleep_ms_max);
            tokio::time::sleep(Duration::from_millis(sleep_ms)).await;
        }
    }
    
    println!("[{}] Application terminated gracefully", Local::now().format("%Y-%m-%d %H:%M:%S"));
    info!("Application terminated gracefully");
    
    Ok(())
}
