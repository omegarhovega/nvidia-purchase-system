# NVIDIA Store Check

A simple Rust script that queries the NVIDIA store and returns the server reply/status.

## Prerequisites

- Rust and Cargo installed
- Internet connection

## Setup

1. Navigate to the `purchase-core/tests` directory
2. Run `cargo build` to compile the project

## Usage

Run the scripts with:

```bash
cargo run --bin nvidia-store-check
```

```bash
cargo run --bin fast-purchase
```

## What it does

The script:
1. Makes an HTTP GET request to https://store.nvidia.com/de-de/geforce/store
2. Uses the same browser headers as in the fast_purchase.py file
3. Prints the status code and response time
4. Saves the response body to a file named `nvidia_store_response.html`

## Output

The script will output information about:
- Request status
- Final URL after redirects
- Response time
- Response body length
- Any errors encountered

The full HTML response will be saved to `nvidia_store_response.html` in the current directory. 