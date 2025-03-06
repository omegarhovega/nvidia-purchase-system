# Cloudflare Challenge page

Token-based Cloudflare Challenge page solution.

This example demonstrates how to bypass the Cloudflare Challenge located on the page https://2captcha.com/demo/cloudflare-turnstile-challenge. The Selenium library is used to automate browser actions and retrieve CAPTCHA parameters. To solve this type of Cloudflare CAPTCHA, it is necessary to send parameters such as pageurl,sitekey, action, data, pagedata, useragent to the 2Captcha API. After receiving the solution result (token), the script automatically uses the received answer on the page.

Note:
When a web page first loads, some JavaScript functions and objects (such as window.turnstile) may already be initialized and executed. If the interception script is launched too late, this may lead to the fact that the necessary parameters will already be lost, or the script simply will not have time to intercept the right moment. Refreshing the page ensures that everything starts from scratch and you trigger the interception at the right time.

Source code: ./examples/cloudflare/cloudflare_challenge_page.py