# DealFlow AI - API Testing Script
# Run this to test your application

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DealFlow AI - API Testing Script  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -UseBasicParsing
Write-Host "Status: $($health.status)" -ForegroundColor Green
Write-Host "App: $($health.app)" -ForegroundColor Green
Write-Host "Total Leads: $($health.total_leads)" -ForegroundColor Green
Write-Host ""

# Test 2: Create a Lead
Write-Host "Test 2: Creating a Lead" -ForegroundColor Yellow
$leadData = @{
    company_name = "TechCorp Inc"
    email = "john@techcorp.com"
    contact_name = "John Smith"
    industry = "Technology"
    company_size = "Medium"
    website = "techcorp.com"
    phone = "+1-555-0100"
} | ConvertTo-Json

$leadResult = Invoke-RestMethod -Uri "http://localhost:8000/api/leads" -Method Post -Body $leadData -ContentType "application/json" -UseBasicParsing
$leadId = $leadResult.lead_id
Write-Host "✅ Lead Created!" -ForegroundColor Green
Write-Host "Lead ID: $leadId" -ForegroundColor Cyan
Write-Host ""

# Test 3: Process Lead with AI Prospecting Agent
Write-Host "Test 3: Processing Lead with ADK Prospecting Agent" -ForegroundColor Yellow
$processResult = Invoke-RestMethod -Uri "http://localhost:8000/api/adk-agents/prospecting/process-lead/$leadId" -Method Post -UseBasicParsing
Write-Host "✅ Lead Processed!" -ForegroundColor Green
Write-Host "Lead Score: $($processResult.lead_score)" -ForegroundColor Cyan
Write-Host "Status: $($processResult.status)" -ForegroundColor Cyan
Write-Host "Analysis: $($processResult.analysis)" -ForegroundColor White
Write-Host ""

# Test 4: Send AI-Generated Outreach Email
Write-Host "Test 4: Sending Outreach with ADK Nurturing Agent" -ForegroundColor Yellow
$outreachResult = Invoke-RestMethod -Uri "http://localhost:8000/api/adk-agents/nurturing/send-outreach/$leadId" -Method Post -UseBasicParsing
Write-Host "✅ Outreach Sent!" -ForegroundColor Green
Write-Host "Deal Created: $($outreachResult.deal_id)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email Preview:" -ForegroundColor Yellow
Write-Host $outreachResult.email_preview -ForegroundColor White
Write-Host ""

# Test 5: Get Pipeline Insights
Write-Host "Test 5: Getting Pipeline Insights from ADK Intelligence Agent" -ForegroundColor Yellow
$insights = Invoke-RestMethod -Uri "http://localhost:8000/api/adk-agents/intelligence/pipeline-insights" -Method Get -UseBasicParsing
Write-Host "✅ Insights Generated!" -ForegroundColor Green
Write-Host ""
Write-Host "PIPELINE ANALYTICS:" -ForegroundColor Cyan
Write-Host "Total Leads: $($insights.report.leads.total)" -ForegroundColor White
Write-Host "Qualified Leads: $($insights.report.leads.qualified)" -ForegroundColor White
Write-Host "Total Deals: $($insights.report.deals.total)" -ForegroundColor White
Write-Host "Pipeline Value: `$$($insights.report.deals.pipeline_value)" -ForegroundColor White
Write-Host "Agent Actions: $($insights.report.agent_performance.total_actions)" -ForegroundColor White
Write-Host ""
Write-Host "Recommendations:" -ForegroundColor Yellow
foreach ($rec in $insights.report.recommendations) {
    Write-Host "  • $rec" -ForegroundColor White
}
Write-Host ""

# Test 6: List All Leads
Write-Host "Test 6: Listing All Leads" -ForegroundColor Yellow
$allLeads = Invoke-RestMethod -Uri "http://localhost:8000/api/leads" -Method Get -UseBasicParsing
Write-Host "✅ Total Leads: $($allLeads.total)" -ForegroundColor Green
Write-Host ""

# Test 7: View All Deals
Write-Host "Test 7: Listing All Deals" -ForegroundColor Yellow
$allDeals = Invoke-RestMethod -Uri "http://localhost:8000/api/deals" -Method Get -UseBasicParsing
Write-Host "✅ Total Deals: $($allDeals.total)" -ForegroundColor Green
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ✅ ALL TESTS COMPLETED!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
