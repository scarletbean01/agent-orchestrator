# Test runner script for Windows PowerShell

Write-Host "Running Agent Orchestrator Tests" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if pytest is installed
$pytestInstalled = Get-Command pytest -ErrorAction SilentlyContinue
if (-not $pytestInstalled) {
    Write-Host "Error: pytest is not installed" -ForegroundColor Red
    Write-Host "Install with: pip install pytest"
    exit 1
}

# Set PYTHONPATH
$env:PYTHONPATH = ".;$env:PYTHONPATH"

# Run tests
pytest cli/tests/ $args

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Tests completed!" -ForegroundColor Green

