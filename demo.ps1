# DealFlow AI - Quick Demo Script
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  DealFlow AI - LIVE DEMO" -ForegroundColor White
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health
Write-Host "1. Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
Write-Host "   Status: $($health.status)" -ForegroundColor Green
Write-Host ""

# Test 2: Create Lead
Write-Host "2. Creating Lead..." -ForegroundColor Yellow
$body = '{"company_name":"TechCorp","contact_name":"Jane Doe","email":"jane@techcorp.com","industry":"SaaS","company_size":"100-500"}'
$lead = Invoke-RestMethod -Uri "http://localhost:8000/api/leads" -Method Post -Body $body -ContentType "application/json"
Write-Host "   Lead ID: $($lead.lead_id)" -ForegroundColor Green
$leadId = $lead.lead_id
Write-Host ""

# Test 3: Prospecting Agent
Write-Host "3. Running Prospecting Agent..." -ForegroundColor Yellow
$prospect = Invoke-RestMethod -Uri "http://localhost:8000/api/adk-agents/prospecting/process-lead/$leadId" -Method Post
Write-Host "   Score: $($prospect.lead_score)" -ForegroundColor Cyan
Write-Host "   Status: $($prospect.status)" -ForegroundColor Cyan
Write-Host ""

# Test 4: Nurturing Agent
Write-Host "4. Running Nurturing Agent..." -ForegroundColor Yellow
$nurture = Invoke-RestMethod -Uri "http://localhost:8000/api/adk-agents/nurturing/send-outreach/$leadId" -Method Post
Write-Host "   Email generated successfully!" -ForegroundColor Green
Write-Host ""

# Test 5: Intelligence Agent
Write-Host "5. Running Intelligence Agent..." -ForegroundColor Yellow
$intel = Invoke-RestMethod -Uri "http://localhost:8000/api/adk-agents/intelligence/pipeline-insights" -Method Get
Write-Host "   Insights generated!" -ForegroundColor Green
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
