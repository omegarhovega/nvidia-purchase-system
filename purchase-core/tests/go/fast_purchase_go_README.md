# Fast Purchase Go Implementation

This is a high-performance Go implementation of the NVIDIA purchase system. It's designed to be as fast as possible while maintaining the same functionality as the original Rust implementation.

## Features

- Uses the Go standard library's HTTP client for maximum performance
- Loads cookies from `captured_cookies.json` (focusing on the CloudFlare clearance cookie)
- Adds all necessary browser fingerprinting headers to avoid detection
- Saves the final HTML page, redirect history, and updated cookies
- Tracks and reports execution time

## Requirements

- Go 1.18 or higher

## Usage

```bash
# Navigate to the go directory
cd purchase-core/tests/go

# Build the Go program
go build fast_purchase.go

# Run with default URL
./fast_purchase

# Or specify a custom URL
./fast_purchase -url="https://marketplace.nvidia.com/de-de/consumer/graphics-cards/"

# Alternatively, use the batch file
run_fast_purchase_go.bat
```

## Performance Considerations

This implementation is optimized for speed by:

1. Using Go's efficient HTTP client with custom transport settings
2. Minimizing memory allocations with pre-allocated buffers and string builders
3. Using sync.Pool for buffer reuse to reduce GC pressure
4. Parallel processing of file operations using goroutines
5. Using efficient map lookups instead of linear searches
6. Optimizing string concatenation with strings.Builder
7. Direct byte manipulation instead of string conversions
8. Custom HTTP transport with optimized connection settings

## Files Created

The program creates the following files in the `shared/scripts` directory:

- `final_page_go.html`: The final HTML page after all redirects
- `redirect_history_go.json`: A record of all redirects that occurred
- `captured_purchase_cookies_go.json`: Updated cookies from the response

## Comparison with Rust Implementation

The Go implementation offers several advantages:

1. Faster startup time
2. Lower memory usage
3. Simpler concurrency model
4. Easier deployment (single binary)
5. No external dependencies

## Troubleshooting

If you encounter any issues:

1. Make sure the `captured_cookies.json` file exists in the `shared/scripts` directory
2. Verify that the file contains a valid `cf_clearance` cookie
3. Check that the URL is accessible and not blocked by Cloudflare
4. Ensure you have proper network connectivity
