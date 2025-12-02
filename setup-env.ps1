# Agent Orchestrator Environment Setup for PowerShell
# Usage: . .\setup-env.ps1  (note the dot at the beginning)

$projectRoot = $PSScriptRoot
$env:PYTHONPATH = "$projectRoot\.orchestra-cli;$env:PYTHONPATH"

Write-Host "[+] PYTHONPATH set for agent orchestrator" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Cyan
Write-Host "  agent status                  # View task status" -ForegroundColor White
Write-Host "  agent start coder 'Task'      # Create new task" -ForegroundColor White
Write-Host "  agent run                     # Run pending tasks" -ForegroundColor White
Write-Host "  agent run --parallel 3        # Run 3 tasks in parallel" -ForegroundColor White
Write-Host "  agent cancel <task_id>        # Cancel a task" -ForegroundColor White
Write-Host "  agent clean completed         # Clean up old tasks" -ForegroundColor White
Write-Host ""

# Create alias for convenience
function agent
{
    $env:PYTHONPATH = "$projectRoot\.orchestra-cli;$env:PYTHONPATH"
    python -m cli $args
}

Write-Host "Alias 'agent' is ready to use!" -ForegroundColor Green
Write-Host ""
