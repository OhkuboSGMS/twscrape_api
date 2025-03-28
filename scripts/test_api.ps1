# PowerShell script to start the API server, send a request using curl, and display the results

# Configuration
$ApiPort = 8000
$Username = "elonmusk"
$TweetLimit = 3
$ApiUrl = "http://localhost:$ApiPort"

# Function to check if a port is in use
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$Port\s+.*LISTENING"
    return $connections.Count -gt 0
}

# Function to start the API server
function Start-ApiServer {
    param (
        [int]$Port
    )
    
    # Check if the port is already in use
    if (Test-PortInUse -Port $Port) {
        Write-Host "Port $Port is already in use. Assuming API server is already running." -ForegroundColor Yellow
        return
    }
    
    # Start the API server in a new PowerShell window
    Write-Host "Starting API server on port $Port..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-Command", "cd '$PSScriptRoot\..'; python -m twscrape_api api 0.0.0.0 $Port" -WindowStyle Normal
    
    # Wait for the server to start
    Write-Host "Waiting for API server to start..." -ForegroundColor Cyan
    $maxRetries = 10
    $retryCount = 0
    $serverStarted = $false
    
    while (-not $serverStarted -and $retryCount -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "$ApiUrl" -Method GET -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $serverStarted = $true
                Write-Host "API server started successfully!" -ForegroundColor Green
            }
        }
        catch {
            $retryCount++
            Write-Host "Waiting for API server to start (attempt $retryCount of $maxRetries)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
    
    if (-not $serverStarted) {
        Write-Host "Failed to start API server after $maxRetries attempts." -ForegroundColor Red
        exit 1
    }
}

# Function to send a request to the API and display the results
function Test-ApiEndpoint {
    param (
        [string]$Endpoint,
        [string]$Username,
        [int]$Limit,
        [string]$Description,
        [switch]$IncludeRetweets,
        [switch]$ExcludePinned,
        [switch]$OnlyMedia,
        [switch]$OnlyLinks
    )
    
    $url = "$ApiUrl$Endpoint`?username_or_url=$Username&limit=$Limit"
    
    # Add filter parameters if specified
    if ($IncludeRetweets) {
        $url += "&include_retweets=true"
    }
    
    if ($ExcludePinned) {
        $url += "&exclude_pinned=true"
    }
    
    if ($OnlyMedia) {
        $url += "&only_media=true"
    }
    
    if ($OnlyLinks) {
        $url += "&only_links=true"
    }
    
    Write-Host "`n===== Testing $Description =====" -ForegroundColor Cyan
    Write-Host "Request URL: $url" -ForegroundColor Gray
    
    try {
        # Use curl to send the request
        Write-Host "`nSending request..." -ForegroundColor Cyan
        $response = curl.exe -s $url
        
        # Display the results
        Write-Host "`nResponse:" -ForegroundColor Green
        $response | ConvertFrom-Json | ConvertTo-Json -Depth 10
    }
    catch {
        Write-Host "Error sending request: $_" -ForegroundColor Red
    }
}

# Main script execution
Write-Host "===== Twitter API Test Script =====" -ForegroundColor Cyan
Write-Host "This script will start the API server and test the endpoints." -ForegroundColor Cyan

# Start the API server
Start-ApiServer -Port $ApiPort

# Wait a bit more to ensure the server is fully ready
Start-Sleep -Seconds 3

# Test the /tweets endpoint with default filters (exclude retweets)
Test-ApiEndpoint -Endpoint "/tweets" -Username $Username -Limit $TweetLimit -Description "Formatted Tweets Endpoint (Default Filters)"

# Test the /tweets endpoint with only media tweets
Test-ApiEndpoint -Endpoint "/tweets" -Username $Username -Limit $TweetLimit -Description "Formatted Tweets Endpoint (Only Media)" -OnlyMedia

# Test the /tweets endpoint with only tweets with links
Test-ApiEndpoint -Endpoint "/tweets" -Username $Username -Limit $TweetLimit -Description "Formatted Tweets Endpoint (Only Links)" -OnlyLinks

# Test the /tweets endpoint with exclude pinned tweets
Test-ApiEndpoint -Endpoint "/tweets" -Username $Username -Limit $TweetLimit -Description "Formatted Tweets Endpoint (Exclude Pinned)" -ExcludePinned

# Test the /tweets/json endpoint with default filters
Test-ApiEndpoint -Endpoint "/tweets/json" -Username $Username -Limit $TweetLimit -Description "Raw JSON Tweets Endpoint (Default Filters)"

Write-Host "`n===== Test Complete =====" -ForegroundColor Green
Write-Host "The API server is still running in the background." -ForegroundColor Yellow
Write-Host "You can access the API documentation at $ApiUrl/docs" -ForegroundColor Yellow
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host
