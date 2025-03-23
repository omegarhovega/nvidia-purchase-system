# NVIDIA Founders Edition Monitor

A minimal Rust script that monitors the NVIDIA Founders Edition inventory API for changes in product availability status.

## Overview

This script monitors the NVIDIA Founders Edition API endpoint and alerts you when there are changes to any of the following product properties:
- `is_active` status
- `product_url`
- `fe_sku`

The script compares the current values with the expected baseline values and sends a desktop notification when changes are detected.

## Features

- Periodically checks the NVIDIA FE API endpoint
- Validates response against expected baseline values
- Desktop notifications for any detected changes
- Configurable check interval
- Verbose logging option
- Customizable API endpoint URL

## Usage

### Building the Application

```bash
cargo build --release
```

The compiled binary will be in `target/release/nvidia-fe-monitor`.

### Running the Application

Basic usage:

```bash
# Run with default settings (checks every 60 seconds)
./target/release/nvidia-fe-monitor
```

With command-line options:

```bash
# Run with custom check interval (e.g., 30 seconds)
./target/release/nvidia-fe-monitor --interval 30

# Run in verbose mode for detailed logging
./target/release/nvidia-fe-monitor --verbose

# Specify a custom API endpoint URL
./target/release/nvidia-fe-monitor --url "https://api.store.nvidia.com/partner/v1/feinventory?status=1&skus=Pro5090FE&locale=DE"
```

### Setting Up Environment for Logging

To see log messages, set the `RUST_LOG` environment variable:

```bash
$env:RUST_LOG="info"; cargo run -- --verbose
```

```bash
# Windows PowerShell
$env:RUST_LOG="info"
./target/release/nvidia-fe-monitor

# Windows Command Prompt
set RUST_LOG=info
.\target\release\nvidia-fe-monitor
```

## Expected API Response

The baseline expected response from the NVIDIA API is:

```json
{
  "success": true,
  "map": null,
  "listMap": [
    {
      "is_active": "false",
      "product_url": "",
      "price": "1000000",
      "fe_sku": "Pro5090FE_DE",
      "locale": "DE"
    }
  ]
}
```

The script will alert you when `is_active`, `product_url`, or `fe_sku` change from their expected values.

## Notifications

When changes are detected, the script will:
1. Log a warning with detailed change information
2. Display a desktop notification that remains visible until dismissed
