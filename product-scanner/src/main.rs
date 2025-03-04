use std::error::Error;
use std::time::Duration;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use rand::Rng;
use chrono::Local;
use log::{info, error, LevelFilter};
use simplelog::{CombinedLogger, Config, TermLogger, WriteLogger, TerminalMode, ColorChoice};
use std::fs::File;
use reqwest;
use config::Config as AppConfig;
use tokio;
use std::env;

mod product_checker;
mod launch_purchase;
mod sound;

use product_checker::{check_nvidia_api, ApiConfig, HeadersConfig, DefaultLinksConfig, RequestConfig, simulate_available_product};
use launch_purchase::PurchaseConfig;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Check for test mode
    let args: Vec<String> = env::args().collect();
    let test_mode = args.len() > 1 && (args[1] == "--test" || args[1] == "--test-error");
    let test_error_mode = args.len() > 1 && args[1] == "--test-error";
    
    // Set up logging
    let log_file = File::create("nvidia_product_checker.log")?;
    CombinedLogger::init(vec![
        TermLogger::new(LevelFilter::Info, Config::default(), TerminalMode::Mixed, ColorChoice::Auto),
        WriteLogger::new(LevelFilter::Info, Config::default(), log_file),
    ])?;
    
    // Load configuration
    let settings = AppConfig::builder()
        .add_source(config::File::with_name("config/default"))
        .build()?;
    
    // Extract configuration values
    let api_url = settings.get_string("url")?;
    let timeout_secs = settings.get_int("request.timeout_secs")? as u64;
    let connect_timeout_secs = settings.get_int("request.connect_timeout_secs")? as u64;
    let max_attempts = settings.get_int("request.max_attempts")? as u32;
    let sleep_ms_min = settings.get_int("request.sleep_ms_min")? as u64;
    let sleep_ms_max = settings.get_int("request.sleep_ms_max")? as u64;
    
    // Extract default links
    let default_link_5080 = settings.get_string("default_links.rtx_5080")?;
    let default_link_5090 = settings.get_string("default_links.rtx_5090")?;
    
    // Extract purchase configuration
    let purchase_enabled = settings.get_bool("purchase.enabled").unwrap_or(false);
    let purchase_product_names: Vec<String> = settings
        .get_array("purchase.product_names")
        .unwrap_or_default()
        .iter()
        .filter_map(|v| v.clone().into_string().ok())
        .collect();
    
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
        url: api_url,
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
        default_links: DefaultLinksConfig {
            rtx_5080: default_link_5080,
            rtx_5090: default_link_5090,
        },
        request: RequestConfig {
            timeout_secs,
            connect_timeout_secs,
            max_attempts,
            sleep_ms_min,
            sleep_ms_max,
        },
    };
    
    // Create purchase configuration
    let purchase_config = PurchaseConfig {
        enabled: purchase_enabled,
        product_names: purchase_product_names,
    };
    
    // Create HTTP client with timeout
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(timeout_secs))
        .connect_timeout(Duration::from_secs(connect_timeout_secs))
        .user_agent(&api_config.headers.user_agent)
        .build()?;
    
    println!("[{}] Configuration loaded successfully", Local::now().format("%Y-%m-%d %H:%M:%S"));
    info!("Configuration loaded successfully");
    
    // If in test mode, run the test and exit
    if test_mode {
        println!("[{}] Running in TEST MODE{}", 
                Local::now().format("%Y-%m-%d %H:%M:%S"),
                if test_error_mode { " (with forced error)" } else { "" });
        info!("Running in TEST MODE{}", if test_error_mode { " (with forced error)" } else { "" });
        
        // Test with RTX 5090
        if let Err(e) = simulate_available_product("GeForce RTX 5090", &purchase_config, test_error_mode).await {
            error!("Failed to simulate product availability: {}", e);
            println!("[{}] Failed to simulate product availability: {}", 
                     Local::now().format("%Y-%m-%d %H:%M:%S"), e);
        }
        
        // Test with a non-configured product
        if let Err(e) = simulate_available_product("Some Other GPU", &purchase_config, false).await {
            error!("Failed to simulate product availability: {}", e);
            println!("[{}] Failed to simulate product availability: {}", 
                     Local::now().format("%Y-%m-%d %H:%M:%S"), e);
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
        
        // Check NVIDIA API
        if let Err(e) = check_nvidia_api(&api_config, &client, &purchase_config, cycle).await {
            error!("Cycle #{} - Failed to check NVIDIA API: {}", cycle, e);
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
