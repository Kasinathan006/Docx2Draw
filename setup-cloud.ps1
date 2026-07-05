####################################################################
# Doc2Draw Cloud Setup Script
# Run this ONCE after you have:
#   1. Deployed the backend to Render
#   2. Connected the frontend repo to Vercel
#
# It will:
#   - Log you into Vercel CLI
#   - Ask for your Render backend URL
#   - Set NEXT_PUBLIC_API_URL and BACKEND_URL in Vercel
#   - Trigger a fresh Vercel redeploy
####################################################################

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Doc2Draw Cloud Setup" -ForegroundColor Cyan  
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login to Vercel
Write-Host "[1/4] Logging into Vercel..." -ForegroundColor Yellow
npx vercel login

# Step 2: Link the project
Write-Host ""
Write-Host "[2/4] Linking Vercel project..." -ForegroundColor Yellow
Set-Location frontend
npx vercel link --yes

# Step 3: Get the Render URL from user
Write-Host ""
Write-Host "[3/4] Setting environment variables..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Enter your Render backend URL (e.g. https://doc2draw-backend.onrender.com):" -ForegroundColor Green
$RENDER_URL = Read-Host "Render URL"

# Remove trailing slash
$RENDER_URL = $RENDER_URL.TrimEnd('/')

Write-Host ""
Write-Host "Setting NEXT_PUBLIC_API_URL = $RENDER_URL" -ForegroundColor Cyan
echo $RENDER_URL | npx vercel env add NEXT_PUBLIC_API_URL production

Write-Host "Setting BACKEND_URL = $RENDER_URL" -ForegroundColor Cyan
echo $RENDER_URL | npx vercel env add BACKEND_URL production

Write-Host ""
Write-Host "[4/4] Triggering redeploy..." -ForegroundColor Yellow
npx vercel --prod

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  DONE! Your site is now live." -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

Set-Location ..
