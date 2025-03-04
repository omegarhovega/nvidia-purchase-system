use std::fs::File;
use std::io::BufReader;
use std::path::Path;
use std::thread;
use std::error::Error;
use log::{info, error};

/// Plays a sound file asynchronously in a separate thread so it doesn't block the main process
pub fn play_sound(sound_name: &str) {
    play_sound_with_options(sound_name, false);
}

/// Plays a sound file with the option to block until it completes
pub fn play_sound_with_options(sound_name: &str, blocking: bool) {
    let sound_path = get_sound_path(sound_name);
    
    if blocking {
        // Play sound synchronously (blocking)
        if let Err(e) = play_sound_internal(&sound_path) {
            error!("Failed to play sound '{}': {}", sound_path, e);
        } else {
            info!("Sound played (blocking): {}", sound_path);
        }
    } else {
        // Spawn a thread to play the sound asynchronously
        thread::spawn(move || {
            if let Err(e) = play_sound_internal(&sound_path) {
                error!("Failed to play sound '{}': {}", sound_path, e);
            } else {
                info!("Sound played: {}", sound_path);
            }
        });
    }
}

/// Plays the buy alert sound when a product is found
pub fn play_purchase_alert() {
    play_sound("alert_buy.mp3");
}

/// Plays the buy alert sound when a product is found, blocking until complete
pub fn play_purchase_alert_blocking() {
    play_sound_with_options("alert_buy.mp3", true);
}

/// Plays the error alert sound when an error occurs
pub fn play_error_alert() {
    play_sound("alert_down.mp3");
}

/// Internal function that actually plays the sound
fn play_sound_internal(path: &str) -> Result<(), Box<dyn Error>> {
    // Initialize audio device
    let (_stream, stream_handle) = rodio::OutputStream::try_default()?;
    let sink = rodio::Sink::try_new(&stream_handle)?;
    
    // Open the audio file
    let file = File::open(path)?;
    let source = rodio::Decoder::new(BufReader::new(file))?;
    
    // Play the sound
    sink.append(source);
    sink.sleep_until_end();
    
    Ok(())
}

/// Gets the full path to a sound file
fn get_sound_path(sound_name: &str) -> String {
    let base_dir = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap_or_else(|| Path::new("."))
        .to_string_lossy()
        .to_string();
    
    format!("{}/shared/assets/sounds/{}", base_dir, sound_name)
}
