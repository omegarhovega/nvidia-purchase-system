# Purchase Core

The Purchase Core component is responsible for executing the actual purchase process when a product is found to be available by the Product Scanner.

## Features

- HTTP request functionality with proper headers for NVIDIA marketplace
- Cookie loading from captured cookies JSON file
- Configurable purchase process with dry-run mode
- Command-line interface for testing

## Usage

### Building

```bash
cd puchase-core
cargo build --release
```

### Running from Command Line

```bash
# Dry run (doesn't actually make a purchase)
$env:RUST_LOG="debug"; .\target\release\purchase-core --dry-run "GeForce RTX 5090" "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=cGGPxfRYyEAQIZcnhxjJN%2FOLLxYo1AzRUQ5%2BCEZexiwFBOSjMwsnanN%2FXJ0oRu2reyKKP2C6CluQlS02NEzu%2F2ZEeqaN2Y3HjoPNaEwG%2BF1fDICdp7GktQpKQe1vxC%2BeMgNZxQF7g1wN3gsXDtXX1pBZH03W%2FC4UHDdyQJGLWD4sjITj4YS2QZfcjYV6oqk5Um4FIB7CBPgPwS4XndSYxrTwF8SPJ%2FnJoknsHS2Pt3mJTgsq171Yz8blP04AmETPm3g7HSDUwyuu7zqFmAG61iIzFkBoy%2BvIq1MrqUPcpBUZlFNbPD%2BtCsVuhLQc6kwQOlzYWoiBUQ%2FJUetzApYEMw%3D%3D"

# Real purchase attempt
./target/release/purchase-core "GeForce RTX 5090" "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/nvidia-geforce-rtx-5090/"

# Specify a custom cookie file
./target/release/purchase-core --cookie-file "/path/to/cookies.json" "GeForce RTX 5090" "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/nvidia-geforce-rtx-5090/"
```

### Integration with Product Scanner

The Purchase Core is automatically called by the Product Scanner when a product is found to be available. The Product Scanner passes the product name and purchase link to the Purchase Core.

## Configuration

The Purchase Core uses the following configuration options:

- `--dry-run`: Don't actually make the purchase, just simulate
- `--cookie-file PATH`: Path to the cookie file (default: ../shared/scripts/captured_cookies.json)

## Implementation Details

The Purchase Core:

1. Loads cookies from the captured_cookies.json file
2. Creates an HTTP client with the required headers
3. Makes a GET request to the purchase URL
4. Analyzes the response to determine if the purchase was successful

The HTTP request includes the following headers:

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7
Referer: https://marketplace.nvidia.com/
Upgrade-Insecure-Requests: 1
sec-ch-ua: "Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: same-origin
sec-gpc: 1
```

## Dependencies

- reqwest: HTTP client
- tokio: Async runtime
- serde: JSON serialization/deserialization
- log: Logging
- chrono: Date and time handling
