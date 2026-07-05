####################################################################
# Fix-Env.ps1 - Set Vercel env vars cleanly via REST API
# No piping = no BOM/newline corruption
####################################################################

$BACKEND_URL = "https://doc2draw-backend.onrender.com"

# Get token from Vercel CLI config
$configPath = "$env:APPDATA\Vercel\auth.json"
if (!(Test-Path $configPath)) {
    $configPath = "$env:LOCALAPPDATA\Vercel\auth.json"
}
$auth = Get-Content $configPath | ConvertFrom-Json
$token = $auth.token

# Get project ID from .vercel/project.json
$projectConfig = Get-Content "frontend\.vercel\project.json" | ConvertFrom-Json
$projectId = $projectConfig.projectId
$teamId = $projectConfig.orgId

Write-Host "Project ID: $projectId" -ForegroundColor Cyan
Write-Host "Backend URL: $BACKEND_URL" -ForegroundColor Cyan

# Function to set an env var via API
function Set-VercelEnv {
    param($name, $value)
    
    $body = @{
        key    = $name
        value  = $value
        type   = "plain"
        target = @("production")
    } | ConvertTo-Json
    
    $url = "https://api.vercel.com/v10/projects/$projectId/env?teamId=$teamId"
    
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body `
        -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
    
    Write-Host "✅ Set $name successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setting environment variables..." -ForegroundColor Yellow
Set-VercelEnv "NEXT_PUBLIC_API_URL" $BACKEND_URL
Set-VercelEnv "BACKEND_URL" $BACKEND_URL

Write-Host ""
Write-Host "Redeploying to production..." -ForegroundColor Yellow
Set-Location frontend
npx vercel --prod --yes
Set-Location ..

Write-Host ""
Write-Host "✅ Done! Env vars are clean (no BOM, no newlines)." -ForegroundColor Green
