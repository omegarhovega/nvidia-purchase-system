import random
# KEY CONFIG VARIABLES

# Store URL for desired graphics card
NVIDIA_URL = "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/?locale=de-de&page=1&limit=12&gpu=RTX%205090&manufacturer=NVIDIA&manufacturer_filter=NVIDIA~1"

# Old Proshop URLs for 5080 to be able to get the cf_clearance cookie
PROSHOP_URLS_5080 = [
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=Y3ccbxb2pHuq5dElEugtOQnlQ4S8UfSLpqrEQE1QkHxoYkLCPVyNhqGcCh3P2B46A%2BT6sQGnIRmgoJ1zpflg0hqwGiS86X8rw%2BlnDai0YpqifOipCfIuT6po27HA0WYaflq1jlmDB0Puye6J%2FNc3ljDr%2Bcq49wSh7tqQc9xiH50ijxrNyMk1zg3U35VqfgJuztP2cLCofTFoa%2BjCA1GdPh3cSmct8x9%2Foj54eEWJ0Pk8A2AhD4Y0ne7CrITnzOLW0k%2BDTP4KyPbEgmC8v5%2FVkVshnUZlhPdSoP9EtDwZ3yD8TtNQrFarxCEdMLsnXNlRUReocTIDRIWuhLxMGATByQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=ZGmF2Itbx52FQ%2B%2Bzkd4SfK63wUZF%2FsA76ZObHzHkqQVXsGtAI0Z2tPljSghaq6n1vURBpnGt9WRIh5g07lWVQrYktGgIHAElB87lZKtmCEH2C4qwfGYk5Mvl5mrvM8%2BnOP8nOGsAEoOib4xl2kxZQkLxH63sIcO%2BB5Oz61aOvWNR%2FFWKVSnuWIl1g4zWSS2qdKuK6PeT86DhKtPr%2BwjRMsm1Vu1gf8OBRXMDnl3HrjWf7PqjcSLYTSRFQRcuibiZBjdqsLqAjFywgESLf2Yh8RcmmBzawn0cBKVeGyrWWFB9Kj0DNwHA8o2x%2FaXniXi4U2qBI%2BWNTqIlcYsYbjP%2B1Q%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=GBKIrKhIKjGZiaEp3dM6dCpB21gNLQqz7sGmP0pbk%2FPoWi49Sy%2FPIbGXcN7Kzk8IL2USzpH0fatKBtyBysEuByYRxanrnL8Bw5j8Z7wN%2FLtWQm7dkmzT0ZL9ufG1M6WlBb1dtrxQ2%2FRsuYsF6KQa9EBFWlgHw8eFGPxaTO4%2FGczsQAcrcs%2BpppRW2U%2FlVLhL1Eup3nas2CLSF%2BNqdUNT7z5mbA%2BgDWOuIJWracJ1UBRGF1saGFss%2FLg1mHHpHP09B6IPDvZG88QbO1VAbMTIvHEqDML2JMgSlSXrYu%2BhF2doEGAqs5I7bOloiYtY6HcVM6bC9xiDa6g4NYf7ZYg1iA%3D%3D",
]

# Old Proshop URLs for 5090 to be able to get the cf_clearance cookie
PROSHOP_URLS_5090 = [
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=Uhgm3Iw%2BgdsjYpUtYecLzX07kCdjGEsfaO9TU26jBH8%2FIdzmXcaRrDSo103ljFbD7lgnLyoM%2ByeNVx%2FhVdMk%2F9hHLVV1rEsmSoo6sSSmlucg9mBhuU03%2FAs53nMAvO5FMMOE5sTU0p10d8z4nkQKOVLJD13VRJNWaoGpHrSi%2FllpHNuKQQlhnb61EYMT%2FSfAlYLcebLzBRP37SS3QmBFFlxolRtN6AwRE23VPjzVDQED9PeBXKlMNcd4qPAfLPSEWVH5WKnhz27OL5C9nRhA1yBJ1mi7Tthdx51VO6%2BM%2FCJ7kCDlIW%2FgvB0LhXoPPOMU0Eq0d65MmPA%2BHeMvXBaa3w%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=DBoN9dv1xUnC0AnAKo1xrvjvWpeQGMDI6itlTZ5Ko%2FdfGthuD%2BHhmfAkZ3dtiJ5zyz9tZyJ9KTcA3W1OdtitVx9p9oAzZaha7Rhzat056UeVQFr2To1NBVguaA6IbkAgtGIzJCnN3jjc8yeKUIThmkNPc8%2BrzMmXLlSmqow108iYL25qbsYhMcr5PnAeBGputnpBN0dpSii9RcpERcNlGExGgEUE%2FrHSgtehG5Ynaf4C0Bftw%2Fglwxar4YZh59UUao3ufJic3iOyv8T7pqptDRsp9vM6TvslnQI7anAFP2w5Ut2GUrciYLg3xTNY5q7QKgMEjg41zAb1g9NkQgXDWQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=NIuab8VFf%2F8x%2BA9d%2F4h68kZunl%2B39oaRC%2B%2BB7pINZIS5XQ8WSy4TTVGUR7ZEcQFkADZPmqfxBJzpgjksr3rwDV3C2KrikEp%2BdreduKrfVpsJJgkJv9Mjy9bqMMumx1Laj0DkbhDNj2UdTNtuNhol7aHBawa915iScBEPVCXIaVALjTiyuCLyZeoYl5nSOwIc%2BYJZ0%2Ffr76bdbdtRUGV2azjnKXdSvZ9mpy002y8Y8eCI%2FJLgIpvixK2UmUa%2BjvSP%2BGKe%2BotbuJi1r%2FWuVZoPr%2FaiOWKyTmXadyuLFd%2B16Q44smMwiLuo4XTLTwHtyhtFSs0%2F9H6MiN58m8DjQPDDag%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=cGGPxfRYyEAQIZcnhxjJN%2FOLLxYo1AzRUQ5%2BCEZexiwFBOSjMwsnanN%2FXJ0oRu2reyKKP2C6CluQlS02NEzu%2F2ZEeqaN2Y3HjoPNaEwG%2BF1fDICdp7GktQpKQe1vxC%2BeMgNZxQF7g1wN3gsXDtXX1pBZH03W%2FC4UHDdyQJGLWD4sjITj4YS2QZfcjYV6oqk5Um4FIB7CBPgPwS4XndSYxrTwF8SPJ%2FnJoknsHS2Pt3mJTgsq171Yz8blP04AmETPm3g7HSDUwyuu7zqFmAG61iIzFkBoy%2BvIq1MrqUPcpBUZlFNbPD%2BtCsVuhLQc6kwQOlzYWoiBUQ%2FJUetzApYEMw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=e97%2BsIN%2Fy5TCBgbJggoLh0Bd968YoxY1Mqn6DYAjZVJRJfpLDYIAvaSjYIjnBc%2FOb3tgl4wZ9h4p05ZPBU%2Fwl3ICDequhyRCQsr5ZuLdTDPrIXQV8ppcJqKErdKBVUPtbDEqlwALOU%2B3djJlQ%2BpRtbqkH%2FqE8%2By6JHstHay2uxyXNKW1ZufsXGmLKgWMv2U%2Bu%2BJqWJ1GFrW07ILRhmjfVEbjrWEBKkyMDJr%2B8cFPu6PodeId%2FHJ6OBeYFmud2G29YExXMIVkP5oUWR3YOuaAawsBu4bT%2FFIWGmqBM5%2FxkEXmJkznEp7WejcPHD5nOmRlS051CXKlEPiUsd%2FAMatoyQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=KKhHB%2BRgii8x9Whv7x6dUL2nbrrv74sLzqeEBwmYZdu03QDimI2NX4xjLmz9%2FU5L2gJesyGEfh8aeX3xmtrfgYzP5a5aQ9a3wuJLMcY0B9lUOkV6qYfjMYl2PKlF%2BgZJK3xp9hwW5JtISujKif7wilHdCCnfTltJ618tLL6Wa7g8XyjGCadvG2VSieua5s4ZLL59n9HNsSK%2FLPGWmv0lAd4LQw6yFLhEGqZV6JQalg9IBj8NORidB9cjPXkq9iHgQYqkID3vdDRhJ50tgy4LQb7%2Frh93x6wvOOhEUGLnMXgkEFMCUowdf3P4WYof1280JemQBZ%2FYuSexVfdCFgwplw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=S7zVHpMFRiSz60DY%2Bi%2FOr1t%2FFiY%2FW%2BA9JU6B0TkLNcftxhk%2F6ytUmxiXzwaiIyl8WbM4gCYvT3McHBk%2Br0i9yxFbztVWnSd%2Bai2dX8nnegGH4qagekFj0wZ%2FGY3dk6KhNkiAIdKwKdDNq6OIqeNlEzTvbdV5XvispuvwTOMqXbuaBMzeZyxEighyqaKeS98Ipp0K4gpG3HyhZ1wgVRjg0W1MxqGcn9w9h48U7AlFVOB1rRT7VgmAngbGxNOwKlTP1q%2BHegA7cShH4f58ZbmCv2r6YkCsC%2F4JoH4bL4aCZzMG1%2BgNY1c5Idl4ghRhKJKCD2IAohR8ECR1BmJDd5WLjw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=HxFI3PyYFsv1XYdAV%2BcuykCMwIfy2vdWLx3x9aac4f1eiglmBQtvSDIbyXjXY2W%2F3nDHVcPrP%2FNF5TpuNb1HJtLyZzE4PJwHIlwRNTbf4njJiSMTOQdLp0Znz6vIRIjdhsnudmiZwWZVV0VnH8slYbUmaXoGahR5IoqlPDgNgmHajPtCcu0hd6iL5vcRYee8%2FU9JvW8KlGQM3MgLuiYJjH2mLlLkVDDrvTxV9bCygQSjiUJlA2%2FVApZKUG1I5DN9vtuWrDUuwduRGJk17lo9w5pbJzcl%2FGuTRnw%2Fm65Un23HzmzoDNpqPE1h5o4bnL5BKf41aIfRXZhlQnC2aqwBmA%3D%3D",
]

# Stale Proshop URL to allow doing the redirect to get the cf_clearance cookie
PROSHOP_URL = random.choice(PROSHOP_URLS_5090)

# Selector for the buy button on product page
NVIDIA_BUY_BUTTON_SELECTOR = "#resultsDiv > div > div > div:nth-child(2) > div.product_detail_78.nv-priceAndCTAContainer > div > div.clearfix.pdc-87.fe-pids > a > button"

# Inject script to mock the NVIDIA API response to be able to follow the stale purchase link and get the cf_clearance cookie
NVIDIA_INJECT_SCRIPT = interceptor_js = """
        console.log('[Interceptor] Mocking NVIDIA API response');
        (function() {
            const mockData = %s;
            const originalXHROpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
                this._url = url;
                return originalXHROpen.apply(this, arguments);
            };
            const originalXHRSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.send = function(body) {
                if (this._url && this._url.includes('api.store.nvidia.com/partner/v1/feinventory')) {
                    Object.defineProperty(this, 'response', {
                        get: function() {
                            return JSON.stringify(mockData);
                        }
                    });
                    Object.defineProperty(this, 'responseText', {
                        get: function() {
                            return JSON.stringify(mockData);
                        }
                    });
                    this.status = 200;
                    this.readyState = 4;
                    if (this.onreadystatechange) { this.onreadystatechange(); }
                    this.dispatchEvent(new Event('readystatechange'));
                    this.dispatchEvent(new Event('load'));
                    return;
                }
                return originalXHRSend.apply(this, arguments);
            };
            const originalFetch = window.fetch;
            window.fetch = function() {
                if (arguments[0] && arguments[0].includes('api.store.nvidia.com/partner/v1/feinventory')) {
                    return Promise.resolve(new Response(JSON.stringify(mockData), {
                        status: 200,
                        headers: {'Content-Type': 'application/json'}
                    }));
                }
                return originalFetch.apply(this, arguments);
            };
        })();
        """

# Inject script to solve the Cloudflare turnstile challenge using 2captcha API
PROSHOP_INJECT_SCRIPT = """
            console.log('[DEBUG] Script injection started');
           
            // Backup interval check
            const i = setInterval(()=>{
              if (window.turnstile) {
                console.log('[DEBUG] Dealing with turnstile');
                clearInterval(i);
                window.turnstile.render = (a,b) => {
                    let p = {
                        type: "TurnstileTaskProxyless",
                        websiteKey: b.sitekey,
                        websiteURL: window.location.href,
                        data: b.cData,
                        pagedata: b.chlPageData,
                        action: b.action,
                        userAgent: navigator.userAgent
                    }
                    console.log("Turnstile parameters:", JSON.stringify(p, null, 2));
                    window.tsCallback = b.callback;
                    return 'foo';
                }
              }
            },50);
            """
