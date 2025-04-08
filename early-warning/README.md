# NVIDIA Founders Edition Monitor

A Rust script that monitors NVIDIA's API for product availability changes and SKU updates.

## Features

- Monitors NVIDIA's inventory API and retailer API endpoints
- Alerts on changes to product status, URLs, or SKUs
- Desktop notifications with sound alerts
- Configurable check interval (default: 10 seconds)
- Detailed logging to both console and file
- Configuration via TOML file

## Configuration

All settings are managed in `config/default.toml`.

## Usage

```bash
# Build the release version
cargo build --release

# Run with default settings
./target/release/nvidia-fe-monitor

# Run with custom interval (in seconds)
./target/release/nvidia-fe-monitor --interval 30

# Run with verbose logging
./target/release/nvidia-fe-monitor --verbose

# Use custom config file
./target/release/nvidia-fe-monitor --config "path/to/config.toml"
```

## Logging

Logs are automatically saved to the `logs` directory with timestamps. To see detailed console output:

```bash
# Windows PowerShell
$env:RUST_LOG="info"
./target/release/nvidia-fe-monitor --verbose
```

## Alerts

The script will alert you when:
- Product availability status changes
- Product URLs are updated
- SKU changes are detected in retailer API
- API response differs from the reference response

Alerts include:
1. Desktop notification
2. Three-tone audio alert
3. Detailed log entries
