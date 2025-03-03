use reqwest::Client;

let client = Client::new();

let response = client
    .get("https://www.example.com")
    .header(USER_AGENT, "MyRustApp/1.0")
    .send()
    .await?;
    
println!("Response status: {}", response.status());
Ok(())