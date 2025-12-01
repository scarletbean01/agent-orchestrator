param(
    [Parameter(Mandatory=$true)][string]$TaskId,
    [Parameter(Mandatory=$false)][string]$Timeout,
    [Parameter(Mandatory=$true)][string]$AgentName,
    [Parameter(Mandatory=$true)][string]$Prompt
)

# Record the PowerShell process ID for tracking
$currentPID = $PID
Set-Content -Path "$taskDir/$TaskId.pid" -Value $currentPID -NoNewline

# 1. Define Paths
$taskDir = ".gemini/agents/tasks"
$doneFile = "$taskDir/$TaskId.done"
$exitCodeFile = "$taskDir/$TaskId.exitcode"
$timeoutFile = "$taskDir/$TaskId.timeout"

# 2. Construct the completion signal message
# We tell the agent to create the .done file when finished
$signalMsg = "Your Task ID is $TaskId. Task: $Prompt. Signal completion by creating $doneFile"

# 3. Prepare opencode arguments
# Start-Process ArgumentList handles quoting for us automatically
$procArgs = @("run", $signalMsg, "--agent", $AgentName)

# 4. Execution Logic
try {
    # Check if a valid timeout was provided
    $useTimeout = (-not [string]::IsNullOrWhiteSpace($Timeout)) -and ($Timeout -ne "null")

    # Start the process
    # -PassThru: Returns the process object so we can track/kill it
    # -NoNewWindow: Ensures stdout/stderr goes to the current console (for logging)
    $p = Start-Process -FilePath "opencode" -ArgumentList $procArgs -PassThru -NoNewWindow

    if ($useTimeout) {
        $timeoutSeconds = [int]$Timeout
        try {
            # Wait for the process up to the limit
            $p | Wait-Process -Timeout $timeoutSeconds -ErrorAction Stop
            
            # If we get here, process finished normally
            $exitCode = $p.ExitCode
            Set-Content -Path $exitCodeFile -Value $exitCode
            exit $exitCode
        }
        catch {
            # Timeout occurred (Wait-Process threw an exception)
            $p | Stop-Process -Force
            
            # Create timeout sentinel file
            $timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
            $json = @{
                timeout = $timeoutSeconds
                timestamp = $timestamp
            } | ConvertTo-Json -Compress
            
            Set-Content -Path $timeoutFile -Value $json
            Write-Output "Task timed out after ${timeoutSeconds}s (Exit Code: 124)"
            
            # Record 124 (standard timeout exit code)
            Set-Content -Path $exitCodeFile -Value "124"
            exit 124
        }
    } else {
        # No timeout - wait indefinitely
        $p | Wait-Process
        
        $exitCode = $p.ExitCode
        Set-Content -Path $exitCodeFile -Value $exitCode
        exit $exitCode
    }
}
catch {
    Write-Output "An unexpected error occurred: $_"
    exit 1
}
