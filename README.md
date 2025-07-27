# 🟩 NVIDIA GPU Purchase System

An automated system for monitoring and purchasing NVIDIA Founders Edition GPUs when they become available. This system is specifically optimized for ProShop (European NVIDIA retail partner) but can be adapted for other retailers.

✅ The script has been successfully used to cart RTX 5090 and RTX 5080 GPUs during several drops. 

Note, however, that while this gives you an advantage, results are not guaranteed and depend on many factors (your connection speed, current retailer server load, traffic detection logic, use of VPNs, proxies, and simple luck). In all likelihood, depending on current demand and availability, several attempts will be needed. 

To be clear, we don't care for scalping and do not engage in it...nor should you.

⚠️ **Important**: Please confirm and respect each vendor's terms of service before using this system.

## 🚀 Quick Start Installation

### 📋 Prerequisites

Before installing, ensure you have:

1. **Python 3.8+** installed on your system
2. **Rust** installed (get it from [rustup.rs](https://rustup.rs/))
3. **Git** for cloning the repository
4. **2captcha API key** (register at [2captcha.com](https://2captcha.com/) - optional, can also be done manually)
5. **Chrome/Chromium browser** (for cookie-prep automation)

### 🔧 Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "+ Fast GPU check/+ Nvidia purchase system"
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Configure browser (optional)**
   ```bash
   # If you want to use a different browser, edit cookie-prep/src/browser.py
   # Change the browser_executable_path to your preferred browser, e.g. under Windows:
   # For Chrome: "C:/Program Files/Google/Chrome/Application/chrome.exe"
   # For Brave: "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
   ```

4. **Build Rust components**
   ```bash
   # Build product scanner
   cd product-scanner
   cargo build --release
   cd ..
   
   # Build early warning system
   cd early-warning
   cargo build --release
   cd ..
   ```

5. **Configure environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env file with your 2captcha API key (optional, for automated captcha solving)
   APIKEY_2CAPTCHA=your_actual_api_key_here
   ```

6. **Test the installation**
   ```bash
   # Run in test mode to verify everything works
   python nvidia_purchase_coordinator.py --test
   ```

### Quick Usage

```bash
# Run the complete system
python nvidia_purchase_coordinator.py

# Run in test mode (safe, no actual purchases)
python nvidia_purchase_coordinator.py --test
```

## 📚 How to Use

When you run `python nvidia_purchase_coordinator.py`, here's what happens:

### 🍪 Phase 1: Initial Cookie Acquisition

1. **Browser Opens**: A Chrome/Chromium browser window will automatically open and navigate to the NVIDIA shop website
2. **Script Injection**: The system injects JavaScript to simulate availability of the selected GPU and activates the purchase link button
3. **Automatic Navigation**: The browser automatically clicks the purchase link (configured for ProShop in this case) which triggers a Cloudflare challenge on the ProShop site
4. **Cloudflare Challenge Handling**: 
   - If you have a 2captcha API key configured: The system automatically solves the Cloudflare challenge
   - If no API key: You'll need to manually solve the Cloudflare challenge in the browser window
5. **Cookie Capture**: Once successful, the system captures and saves all cookies (especially `cf_clearance`) to `shared/scripts/captured_cookies.json`

**Potential Issues During Cookie Acquisition:**
- ⚠️ **VPN Detection**: Cloudflare may recognize and block VPN traffic
- ⚠️ **Server Overload**: Retailer servers may be overwhelmed during high-traffic periods
- ⚠️ **Rate Limiting**: Too many requests may trigger additional protection measures
- 🍀 **Lucky Direct Purchase**: If a GPU is actually live during this process, you might successfully purchase it immediately!

### 👀 Phase 2: Continuous Monitoring

Once cookies are acquired, the system enters monitoring mode:

1. **Early Warning System**: Monitors NVIDIA API for baseline changes that indicate upcoming releases and warns. Nvidia likes to change the SKU of the GPU for each drop (sometimes days before, sometimes minutes) which means that the scanner will have to be updated to not track the wrong API endpoint. Therefore, if a SKU change is detected, you need to immediately update the `fe_inventory_url` in the `product-scanner/config/default.toml` file to allow the purchase script to track the new correct SKU. Also update the `skus.list` and `fe_inventory_url` in the `early-warning/config/default.toml` to the new values. After a change alert, the new values can e.g. found in NVIDIA's product API (for Germany e.g. https://api.nvidia.partners/edge/product/search?page=1&limit=9&locale=de-de&category=GPU&manufacturer=NVIDIA&manufacturer_filter=NVIDIA~1).
2. **Product Scanner**: Continuously checks for actual product availability
3. **Cookie Refresh**: Automatically refreshes authentication cookies every 12-15 minutes
4. **Audio Alerts**: Plays sound notifications for important events

### 💳 Phase 3: Purchase Attempt

When a GPU becomes available:

1. **Instant Response**: The system immediately attempts to add the GPU to cart
2. **Cookie Authentication**: Uses the stored `cf_clearance` cookie for authenticated access
3. **Cart Success**: If successful, the updated session cookie is saved to `shared/scripts/captured_cookies.json`. If the folder creation fails, manually add the shared/scripts folder to the main project folder.
4. **Manual Checkout**: You copy the `cf_clearance` cookie to your browser, navigate to ProShop, click on the cart and complete the purchase manually (cookies are usually valid for around 10 minutes so you have enough time to complete the purchase)

### 🔍 Monitoring the Process

- **Console Output**: Real-time status updates and important events
- **Log File**: Detailed logging saved to `coordinator.log`
- **Audio Alerts**: Different sounds for availability, errors, and warnings
- **Component Status**: Automatic restart of failed components

### 🔧 Key Settings

#### `product-scanner/config/default.toml`
- **`fe_inventory_url`**: NVIDIA API endpoint for checking product availability (includes SKU and locale). Needs to be updated after a SKU change is detected (see `early-warning`)
- **`timeout_secs`**: API request timeout (default: 30 seconds)
- **`max_attempts`**: Maximum retry attempts for failed requests (default: 4)
- **`sleep_ms_min/max`**: Request interval randomization (1000-1100ms)

#### `early-warning/config/default.toml`
- **`fe_inventory_url`**: Same API endpoint as product scanner. Needs to be updated after a SKU change is detected (see `early-warning`)
- **`retailers_url`**: NVIDIA partners API for broader monitoring
- **`skus.list`**: Array of SKUs to monitor (e.g., "PROFESHOP5090", "PRO5080FESHOP"); NOTE: after an SKU change is detected, you need to update to the new SKUs in this file to track new changes
- **`reference`**: Baseline response values for change detection

#### `cookie-prep/src/config.py`
- **`NVIDIA_URL`**: NVIDIA marketplace URL for the desired GPU model (country code "de-de" can be changed to other countries)
- **`PROSHOP_URLS_5070/5080/5090`**: Arrays of ProShop purchase URLs from previous drop which are used by the cookie-prep inject script to unmask the purchase link on the Nvidia website (can be updated manually with newer links)
- **`PROSHOP_URL`**: Set to desired GPU model (5070/5080/5090) you are interested in

#### `nvidia_purchase_coordinator.py`
- **Cookie refresh interval**: 12-15 minutes (randomized, line 438)
- **Sound patterns**: Customizable audio alerts for different events (lines 66-72)
  - `product_available`: Three ascending tones
  - `early_warning`: Single long tone
  - `api_error/cookie_error`: Two descending tones
- **Silent mode**: `--silent` flag to disable audio alerts
- **File paths**: Locations for components and cookie storage

## 📁 Project Structure

This project is organized into four main components:

1. **product-scanner** (Rust): Product availability monitoring and automated purchase logic
   - NVIDIA API monitoring
   - Product tracking
   - Availability notifications
   - Automatic purchase function
   - Test mode for validating purchase functionality

2. **cookie-prep** (Python): Cookie and session management
   - Browser automation to solve Cloudflare challenges
   - Automatic cookie acquisition and renewal
   - Captures and manages cf_clearance cookie for direct purchase access

3. **nvidia_purchase_coordinator.py** (Python): Top-level coordination
   - Orchestrates all system components
   - Manages cookie refreshes on a schedule
   - Starts and monitors product scanner
   - Enhanced logging with real-time cookie-prep output capture
   - Sound alerts for important events (availability, errors)

4. **early-warning** (Rust): Monitors for changes in product status before official release
   - Monitors baseline NVIDIA API values
   - Alerts when changes are detected in product status

## ⚙️ Configuration

The system uses TOML files for Rust components and Python configuration files:

### Product Scanner Configuration

Located at `product-scanner/config/default.toml`

The scanner configuration controls:
- API endpoints and timeouts
- Request headers and user agent
- Retry parameters
- Sleep intervals between checks

### Early Warning Configuration

Located at `early-warning/config/default.toml`

The monitoring configuration controls:
- API endpoints for inventory and retailer checks
- SKUs to monitor for availability
- Reference response for comparison

### Cookie Preparation Configuration

Located in `cookie-prep/src/config.py`

The cookie configuration controls:
- Browser type and executable path
- Cookie refresh interval
- 2Captcha API key for automated purchasing

### Coordinator Configuration

Configuration is handled directly in `nvidia_purchase_coordinator.py`

The coordinator configuration controls:
- Component lifecycle and communication
- Unified logging and monitoring
- Configurable sound alert patterns
- Cookie refresh intervals

### Running Components Individually

#### Running the Product Scanner Directly

```bash
# Run the product scanner in normal mode
cd product-scanner
cargo run
```

The product scanner will:
1. Monitor the NVIDIA API for product availability
2. When a product becomes available, it will automatically initiate the purchase process

### Running Cookie Preparation Manually

```bash
# From the cookie-prep directory
cd cookie-prep/src
python main.py
```

### Test Mode

The product scanner includes a robust test mode that can be activated with the `--test` command-line argument:

```bash
# Run the product scanner in test mode
cd product-scanner
cargo run --bin product-scanner --  --test
```

When running in test mode, the scanner will:
1. Simulate availability for configured products
2. Test the purchase initiation process by calling the purchase mechanism
3. Verify that the product list in configuration is correctly processed
4. Test that purchases are only attempted for configured products
5. Exit after completing the tests

This test mode is useful for:
- Verifying that your purchase configuration is correct
- Testing the complete purchase flow without waiting for actual product availability
- Confirming that the integration between components works as expected

### Stopping the System

Press `Ctrl+C` to gracefully stop all components.

## ⚙️ Implementation Details

### System Architecture

The system operates as a pipeline:

1. **Cookie Preparation**: Obtains and maintains valid Cloudflare cookies
2. **Product Scanner**: Continuously monitors for product availability
3. **Purchase Process**: When a product is available, automatically attempts to purchase it

### Component Integration

- When the product scanner detects an available product, it calls the purchase_method.py script with the purchase link
- The coordinator script ensures cookies are constantly refreshed to maintain session validity
- All components share cookies through the shared/scripts/captured_cookies.json file

### Product Scanner

The product scanner consists of three main modules:

1. **main.rs**: Application setup, configuration loading, and main loop
   - Handles command-line arguments including test mode
   - Loads configuration from default.toml
   - Sets up logging and error handling
   - Manages the main monitoring loop

2. **product_checker.rs**: API interaction and product availability checking
   - Makes HTTP requests to the NVIDIA API
   - Parses API responses to check product availability
   - Returns product links when products are available
   - Includes test functionality to simulate available products

3. **launch_purchase.rs**: Purchase initiation when products are available
   - Controls purchase behavior through the PurchaseConfig struct
   - Determines which products should trigger purchase attempts
   - Launches the purchase process by calling the Python purchase script
   - Provides logging and error handling for purchase attempts

### Purchase Core

The purchase core component handles the actual purchase process:

1. **purchase_method.py**: 
   - Loads cookies from shared/scripts/captured_cookies.json
   - Makes authenticated requests to purchase links
   - Follows redirects and maintains session state
   - Logs results and saves updated cookies

### Cookie Preparation

The cookie-prep component handles browser automation to solve Cloudflare challenges:

1. **session_manager.py**:
   - Uses browser automation to navigate to NVIDIA website
   - Handles Cloudflare challenges and CAPTCHAs
   - Saves cookies to shared/scripts/captured_cookies.json

### Coordinator

The coordinator (nvidia_purchase_coordinator.py) orchestrates the entire system:

1. Handles startup sequence:
   - First runs session_manager to get initial cookies
   - Then starts the product scanner

2. Manages runtime operations:
   - Runs cookie refresh on a schedule (12-15 minute intervals)
   - Monitors product scanner health
   - Provides consolidated logging
   - Captures and displays cookie-prep output in real-time

3. Handles shutdown:
   - Gracefully stops all components

## 🔧 Potetnial improvements:
- Automated SKU updates after a detected change
- Including logic for other retail partners