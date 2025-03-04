package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// Cookie represents a browser cookie
type Cookie struct {
	Name   string  `json:"name"`
	Value  string  `json:"value"`
	Domain *string `json:"domain,omitempty"`
}

// CookieData represents the structure of the captured_cookies.json file
type CookieData struct {
	Timestamp string   `json:"timestamp"`
	Cookies   []Cookie `json:"cookies"`
}

// Redirect represents a single HTTP redirect
type Redirect struct {
	From       string `json:"from"`
	To         string `json:"to"`
	StatusCode int    `json:"status_code"`
}

// RedirectHistory represents the history of redirects during a request
type RedirectHistory struct {
	Timestamp string     `json:"timestamp"`
	FinalURL  string     `json:"final_url"`
	Redirects []Redirect `json:"redirects"`
}

// bufferPool is a pool of bytes.Buffer objects for reuse
var bufferPool = sync.Pool{
	New: func() interface{} {
		return new(bytes.Buffer)
	},
}

// getSharedScriptsPath returns the path to the shared scripts directory
func getSharedScriptsPath() string {
	// Get current working directory
	currentDir, err := os.Getwd()
	if err != nil {
		fmt.Printf("[ERROR] Failed to get current directory: %v\n", err)
		return ""
	}

	// Navigate up to find the root directory
	// From purchase-core/tests/go we need to go up three levels to reach the root
	rootDir := filepath.Dir(filepath.Dir(filepath.Dir(currentDir)))
	return filepath.Join(rootDir, "shared", "scripts")
}

// getTimestamp returns the current timestamp in ISO format
func getTimestamp() string {
	return time.Now().Format("2006-01-02T15:04:05")
}

// fastPurchase attempts to make a purchase request to the given URL
func fastPurchase(purchaseURL string) (bool, error) {
	// Start timing
	startTime := time.Now()

	// Load cookies from file - use a more efficient file reading method
	cookiesPath := filepath.Join(getSharedScriptsPath(), "captured_cookies.json")
	fmt.Printf("[INFO] Loading cookies from %s\n", cookiesPath)

	// Use os.ReadFile for more efficient file reading
	cookieFile, err := os.ReadFile(cookiesPath)
	if err != nil {
		return false, fmt.Errorf("failed to read cookie file: %w", err)
	}

	var cookieData CookieData
	// Use json.Unmarshal directly on the byte slice to avoid string conversion
	if err := json.Unmarshal(cookieFile, &cookieData); err != nil {
		return false, fmt.Errorf("failed to parse cookie file: %w", err)
	}

	fmt.Printf("[INFO] Loaded %d cookies from %s\n", len(cookieData.Cookies), cookiesPath)

	// Check for CloudFlare clearance cookie - using a map for O(1) lookup
	cookieMap := make(map[string]string, len(cookieData.Cookies))
	for _, cookie := range cookieData.Cookies {
		cookieMap[cookie.Name] = cookie.Value
	}

	cfClearance, hasClearance := cookieMap["cf_clearance"]
	if !hasClearance || cfClearance == "" {
		fmt.Println("[ERROR] No Cloudflare clearance cookie found")
		return false, nil
	}

	preview := cfClearance
	if len(cfClearance) > 10 {
		preview = cfClearance[:10] + "..."
	}
	fmt.Printf("[INFO] Found cf_clearance cookie: %s\n", preview)

	// Create a custom transport for better performance
	transport := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 100,
		MaxConnsPerHost:     100,
		IdleConnTimeout:     90 * time.Second,
		TLSHandshakeTimeout: 10 * time.Second,
		DisableCompression:  true, // We'll handle compression ourselves if needed
	}

	// Create a custom HTTP client with the optimized transport
	client := &http.Client{
		Timeout:   60 * time.Second,
		Transport: transport,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			// Allow redirects but keep track of them
			return nil
		},
	}

	// Create request - pre-allocate the headers map
	req, err := http.NewRequest("GET", purchaseURL, nil)
	if err != nil {
		return false, fmt.Errorf("failed to create request: %w", err)
	}

	// Add cookies to the request - pre-allocate the string builder
	var allCookiesBuilder strings.Builder
	allCookiesBuilder.Grow(1024) // Pre-allocate 1KB which should be enough for most cookie strings
	
	first := true
	for _, cookie := range cookieData.Cookies {
		if !first {
			allCookiesBuilder.WriteString("; ")
		} else {
			first = false
		}
		allCookiesBuilder.WriteString(cookie.Name)
		allCookiesBuilder.WriteString("=")
		allCookiesBuilder.WriteString(cookie.Value)
	}
	
	req.Header.Set("Cookie", allCookiesBuilder.String())

	// Set browser fingerprinting headers - MUST match original
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
	req.Header.Set("Accept-Language", "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7")
	req.Header.Set("Referer", "https://marketplace.nvidia.com/")
	req.Header.Set("Upgrade-Insecure-Requests", "1")
	req.Header.Set("sec-ch-ua", "\"Not(A:Brand\";v=\"99\", \"Brave\";v=\"133\", \"Chromium\";v=\"133\"")
	req.Header.Set("sec-ch-ua-mobile", "?0")
	req.Header.Set("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Set("sec-fetch-dest", "document")
	req.Header.Set("sec-fetch-mode", "navigate")
	req.Header.Set("sec-fetch-site", "same-origin")
	req.Header.Set("sec-gpc", "1")

	fmt.Printf("[INFO] Making request to %s\n", purchaseURL)

	// Make the request
	resp, err := client.Do(req)
	if err != nil {
		return false, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	// Store important information
	status := resp.StatusCode
	finalURL := resp.Request.URL.String()

	// Extract cookies from response headers - pre-allocate the slice
	updatedCookies := make([]Cookie, 0, len(resp.Cookies()))
	for _, cookie := range resp.Cookies() {
		domain := cookie.Domain
		updatedCookies = append(updatedCookies, Cookie{
			Name:   cookie.Name,
			Value:  cookie.Value,
			Domain: &domain,
		})
	}

	// Print the final URL after all redirects
	fmt.Printf("[INFO] Final URL after redirects: %s\n", finalURL)

	// Get response body - use a buffer pool for better memory management
	buf := bufferPool.Get().(*bytes.Buffer)
	defer bufferPool.Put(buf)
	buf.Reset()
	_, err = io.Copy(buf, resp.Body)
	if err != nil {
		return false, fmt.Errorf("failed to read response body: %w", err)
	}
	
	responseBody := buf.Bytes()

	// Save files in parallel using goroutines
	var wg sync.WaitGroup
	var saveErrors []error
	var errorMutex sync.Mutex

	// Save the final HTML page
	wg.Add(1)
	go func() {
		defer wg.Done()
		htmlOutputPath := filepath.Join(getSharedScriptsPath(), "final_page_go.html")
		if err := os.WriteFile(htmlOutputPath, responseBody, 0644); err != nil {
			errorMutex.Lock()
			saveErrors = append(saveErrors, fmt.Errorf("failed to save HTML: %w", err))
			errorMutex.Unlock()
			return
		}
		fmt.Printf("[INFO] Saved final page HTML to %s\n", htmlOutputPath)
	}()

	// Create redirect history
	redirectHistory := RedirectHistory{
		Timestamp: getTimestamp(),
		FinalURL:  finalURL,
		Redirects: []Redirect{},
	}

	// Save redirect history
	wg.Add(1)
	go func() {
		defer wg.Done()
		redirectsOutputPath := filepath.Join(getSharedScriptsPath(), "redirect_history_go.json")
		redirectJSON, err := json.MarshalIndent(redirectHistory, "", "  ")
		if err != nil {
			errorMutex.Lock()
			saveErrors = append(saveErrors, fmt.Errorf("failed to marshal redirect history: %w", err))
			errorMutex.Unlock()
			return
		}
		if err := os.WriteFile(redirectsOutputPath, redirectJSON, 0644); err != nil {
			errorMutex.Lock()
			saveErrors = append(saveErrors, fmt.Errorf("failed to save redirect history: %w", err))
			errorMutex.Unlock()
			return
		}
		fmt.Printf("[INFO] Saved redirect history to %s\n", redirectsOutputPath)
	}()

	// Combine original cookies with any new ones - using the map we already created
	for _, cookie := range updatedCookies {
		cookieMap[cookie.Name] = cookie.Value
	}

	// Convert map back to slice
	combinedCookies := make([]Cookie, 0, len(cookieMap))
	for name, value := range cookieMap {
		combinedCookies = append(combinedCookies, Cookie{
			Name:  name,
			Value: value,
		})
	}

	// Save updated cookies
	wg.Add(1)
	go func() {
		defer wg.Done()
		outputData := CookieData{
			Timestamp: getTimestamp(),
			Cookies:   combinedCookies,
		}

		cookiesOutputPath := filepath.Join(getSharedScriptsPath(), "captured_purchase_cookies_go.json")
		cookieJSON, err := json.MarshalIndent(outputData, "", "  ")
		if err != nil {
			errorMutex.Lock()
			saveErrors = append(saveErrors, fmt.Errorf("failed to marshal cookie data: %w", err))
			errorMutex.Unlock()
			return
		}
		if err := os.WriteFile(cookiesOutputPath, cookieJSON, 0644); err != nil {
			errorMutex.Lock()
			saveErrors = append(saveErrors, fmt.Errorf("failed to save cookies: %w", err))
			errorMutex.Unlock()
			return
		}
		fmt.Printf("[INFO] Saved cookies to %s\n", cookiesOutputPath)
	}()

	// Wait for all file operations to complete
	wg.Wait()

	// Check if any errors occurred during file operations
	if len(saveErrors) > 0 {
		return false, fmt.Errorf("errors during file operations: %v", saveErrors)
	}

	// Check for ASP.NET_SessionId cookie
	aspSession, hasAspSession := cookieMap["ASP.NET_SessionId"]
	if hasAspSession && aspSession != "" {
		fmt.Printf("[INFO] Found ASP.NET_SessionId cookie: %s\n", aspSession)
	}

	// Calculate and print execution time
	executionTime := time.Since(startTime)
	fmt.Printf("[INFO] Request completed in %v\n", executionTime)

	// Success if we got a 200 OK status
	return status == http.StatusOK, nil
}

func main() {
	// Parse command line arguments
	purchaseURL := flag.String("url", "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D", "URL to attempt purchase from")
	flag.Parse()

	fmt.Println("[INFO] Starting fast purchase process...")
	success, err := fastPurchase(*purchaseURL)
	if err != nil {
		fmt.Printf("[ERROR] Purchase process failed: %v\n", err)
		os.Exit(1)
	}

	if success {
		fmt.Println("[SUCCESS] Purchase process completed successfully")
	} else {
		fmt.Println("[WARNING] Purchase process completed with warnings")
	}
}
