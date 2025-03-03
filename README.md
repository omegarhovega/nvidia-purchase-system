# NVIDIA GPU Purchase System

An automated system for monitoring and purchasing NVIDIA GPUs when they become available.

## Project Structure

This project is organized into three main components:

1. **purchase-core** (Rust): Core purchasing functionality

   - HTTP client handling
   - Cookie management
   - Purchase automation

2. **product-scanner** (Rust): Product availability monitoring

   - API monitoring
   - Product tracking
   - Availability notifications

3. **cookie-prep** (Python): Cookie and session management
   - Use script to incject to nvidia shop homepage and show button using old purchase link
   - Follow old purchase link Using 2Captcha to solve Cloudflare challenge
   - Obtain and save cf_clearance cookie

## Setup Instructions

### Prerequisites

- Rust (stable channel)
- Python 3.8+
- Required dependencies (see component-specific READMEs)

### Installation

1. Clone this repository
2. Set up the Rust components:
   ```
   cd purchase-core
   cargo build
   cd ../product-scanner
   cargo build
   ```
3. Set up the Python component:
   ```
   cd cookie-prep
   pip install -r requirements.txt
   ```

## Usage

See the documentation in the `docs` directory for detailed usage instructions.

## Development

Each component can be developed and tested independently. See the component-specific
documentation for development workflows.

## License

[Specify license information]
