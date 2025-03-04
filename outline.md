# Todo:
- Add check for API fields digitalriver and stock >0 as separate fallbacks (then follow direct purchase url)
- Add sounds
- Simplify files


# Test
Ran it without vpn and much faster (3.5 vs 10.2 sec)?

PS C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\product-scanner> cargo run -- --test
   Compiling product-scanner v0.1.0 (C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\product-scanner)
warning: function `play_purchase_alert` is never used
  --> src\sound.rs:37:8
   |
37 | pub fn play_purchase_alert() {
   |        ^^^^^^^^^^^^^^^^^^^
   |
   = note: `#[warn(dead_code)]` on by default

warning: `product-scanner` (bin "product-scanner") generated 1 warning
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 2.12s
     Running `target\debug\product-scanner.exe --test`
[2025-03-04 15:39:53] Configuration loaded successfully
14:39:53 [INFO] Configuration loaded successfully
[2025-03-04 15:39:53] Running in TEST MODE
14:39:53 [INFO] Running in TEST MODE

[2025-03-04 15:39:53] 🧪 TEST MODE: Simulating product availability for 'GeForce RTX 5090'
[2025-03-04 15:39:53] 🧪 TEST MODE: Product 'GeForce RTX 5090' is available, launching purchase process
14:39:53 [INFO] found the format marker [ff, fb] @ 0+2 bytes.
14:39:53 [INFO] estimating duration from bitrate, may be inaccurate for vbr files
14:39:59 [INFO] Sound played (blocking): C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system/shared/assets/sounds/alert_buy.mp3
14:39:59 [INFO] PURCHASE ATTEMPT - Product: GeForce RTX 5090, Link: https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D
[2025-03-04 15:39:59] 🚀 LAUNCHING PURCHASE PROCESS FOR: GeForce RTX 5090
[2025-03-04 15:39:59] 🔗 Product Link: https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D
[2025-03-04 15:39:59] ⏳ Starting purchase process with purchase_method.py
14:39:59 [INFO] Running Python script: "C:\\Users\\Admin\\Documents\\Code\\Fast GPU check\\Nvidia purchase system\\purchase-core\\src\\purchase_method.py"
14:40:03 [INFO] Purchase script executed successfully: [INFO] Using purchase URL from command-line argument: https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D
[INFO] Loaded 19 cookies from C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_cookies.json
[INFO] Found cf_clearance cookie: z7b2E3onfb...
[INFO] Making request to https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D
[INFO] Final URL after redirects: https://marketplace.nvidia.com/de-de/consumer/
[INFO] Saved final page HTML to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\final_page.html
[INFO] Saved redirect history to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\redirect_history.json
[INFO] Saved cookies to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_purchase_cookies.json
[INFO] Found ASP.NET_SessionId cookie: gwwiembevfvzucxpzusxnvms
[INFO] Request completed with status 200 in 3.57s
[INFO] Purchase attempt completed successfully!

[2025-03-04 15:39:59] ✅ Purchase process completed successfully
[2025-03-04 15:39:59] Output: [INFO] Using purchase URL from command-line argument: https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D
[INFO] Loaded 19 cookies from C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_cookies.json
[INFO] Found cf_clearance cookie: z7b2E3onfb...
[INFO] Making request to https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D
[INFO] Final URL after redirects: https://marketplace.nvidia.com/de-de/consumer/
[INFO] Saved final page HTML to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\final_page.html
[INFO] Saved redirect history to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\redirect_history.json
[INFO] Saved cookies to C:\Users\Admin\Documents\Code\Fast GPU check\Nvidia purchase system\shared\scripts\captured_purchase_cookies.json
[INFO] Found ASP.NET_SessionId cookie: gwwiembevfvzucxpzusxnvms
[INFO] Request completed with status 200 in 3.57s
[INFO] Purchase attempt completed successfully!

[2025-03-04 15:40:03] 🧪 TEST MODE: ✅ Purchase successfully launched for 'GeForce RTX 5090'

[2025-03-04 15:40:03] 🧪 TEST MODE: Simulating product availability for 'Some Other GPU'
[2025-03-04 15:40:03] 🧪 TEST MODE: Product 'Some Other GPU' would not trigger a purchase (not in configured product list)
[2025-03-04 15:40:03] Test completed, exiting
14:40:03 [INFO] Test completed, exiting

# Multi-Component Project Structure for Automated Purchase System

Organize this professional multi-language project in VSCode:

```
purchase-system/
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
├── docker-compose.yml        # Optional: for containerized deployment
├── .vscode/                  # VSCode configuration
│   ├── settings.json         # Editor settings
│   ├── launch.json           # Debug configurations
│   └── extensions.json       # Recommended extensions
│
├── purchase-core/            # Main Rust purchase component
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs           # Entry point
│   │   ├── http_client.rs    # HTTP handling
│   │   ├── cookie_manager.rs # Cookie management
│   │   ├── error.rs          # Error handling
│   │   └── config.rs         # Configuration
│   ├── tests/                # Integration tests
│   └── examples/             # Example usage
│
├── product-scanner/          # Rust API scanner component
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs           # Entry point
│   │   ├── api_client.rs     # API monitoring 
│   │   ├── product.rs        # Product models
│   │   ├── scheduler.rs      # Scan scheduling
│   │   └── notification.rs   # Availability notifications
│   └── tests/                # Tests
│
├── cookie-prep/              # Python cookie preparation
│   ├── pyproject.toml        # Python package config
│   ├── requirements.txt      # Dependencies
│   ├── cookie_prep/
│   │   ├── __init__.py
│   │   ├── main.py           # Entry point
│   │   ├── cookie_capture.py # Cookie acquisition
│   │   ├── cookie_export.py  # Format conversion
│   │   └── utils.py          # Utilities
│   └── tests/                # Python tests
│
├── shared/                   # Shared resources
│   ├── schemas/              # Data schemas
│   │   ├── cookies.json      # Cookie format schema
│   │   └── product.json      # Product schema
│   ├── scripts/              # Utility scripts
│   │   ├── setup.sh          # Environment setup
│   │   └── deploy.sh         # Deployment script
│   └── config/               # Configuration templates
│       ├── logging.yaml      # Logging configuration
│       └── defaults.json     # Default settings
│
└── docs/                     # Documentation
    ├── architecture.md       # System architecture
    ├── setup.md              # Setup instructions
    ├── usage.md              # Usage guide
    └── diagrams/             # Architectural diagrams
```

## Professional Practices

1. **Inter-Component Communication:**
   - Use well-defined file formats for cookie exchange
   - Implement a clean CLI interface for component interaction
   - Consider using a lightweight IPC mechanism if needed

2. **Development Workflow:**
   - Create a `Makefile` or similar to standardize common tasks
   - Use separate virtual environments for Python components
   - Set up consistent formatting and linting across languages

3. **Configuration Management:**
   - Use environment variables for sensitive configuration
   - Share common configuration formats between components
   - Implement hierarchical configuration (defaults → file → env → CLI)

4. **Workspace Setup:**
   - Configure VSCode workspace settings in `.vscode/settings.json`
   - Create language-specific debug configurations
   - Set up appropriate extensions for both Rust and Python

5. **Testing Strategy:**
   - Implement unit tests for each component
   - Create integration tests that verify component interactions
   - Add mocks for external services (shop API)

6. **Dependency Management:**
   - Lock dependencies with Cargo.lock and requirements.txt
   - Document minimum version requirements
   - Consider vendoring critical dependencies

7. **Continuous Integration:**
   - Add GitHub Actions or similar CI configuration
   - Implement automatic testing for both Rust and Python
   - Add linting and formatting checks

This structure maintains clear separation of concerns while providing a cohesive project organization. Each component has its own directory with dedicated resources, making it easy to work on individual parts while maintaining the overall system architecture.