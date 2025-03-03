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

mod product_checker;
use product_checker::{check_nvidia_api, ApiConfig, HeadersConfig, DefaultLinksConfig, RequestConfig};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
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
    
    // Extract default links
    let default_link_5080 = settings.get_string("default_links.rtx_5080")?;
    let default_link_5090 = settings.get_string("default_links.rtx_5090")?;
    
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
        },
    };
    
    // Create HTTP client with timeout
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(timeout_secs))
        .connect_timeout(Duration::from_secs(connect_timeout_secs))
        .user_agent(&api_config.headers.user_agent)
        .build()?;
    
    println!("[{}] Configuration loaded successfully", Local::now().format("%Y-%m-%d %H:%M:%S"));
    info!("Configuration loaded successfully");
    
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
        if let Err(e) = check_nvidia_api(&api_config, &client, cycle).await {
            error!("Cycle #{} - Failed to check NVIDIA API: {}", cycle, e);
        }
        
        // Random sleep between 0.5 and 1 second
        if running.load(Ordering::SeqCst) {
            let sleep_ms = rng.gen_range(500..1000);
            tokio::time::sleep(Duration::from_millis(sleep_ms)).await;
        }
    }
    
    println!("[{}] Application terminated gracefully", Local::now().format("%Y-%m-%d %H:%M:%S"));
    info!("Application terminated gracefully");
    
    Ok(())
}
