---
description: "Retry a failed task: /agent:retry <task_id> [max_retries] [--auto]"
agent: build
---
You are the Task Retry Manager.

**GOAL:** Create a retry for a failed task with proper tracking and auto-retry support.

**INPUTS:**
- Task ID: $1 (required)
- Max Retries: $2 (default: 3 if not provided or if "--auto")
- Auto Retry Flag: $3 (check if "--auto" is present in arguments)

**STEPS:**
1.  **Validate Task:**
    - Check if `.gemini/agents/tasks/$1.json` exists
    - If not found, report "Task $1 not found." and exit
    - Read the JSON file
    - If status is not "failed", report "Task $1 is not in failed state (current: <status>). Only failed tasks can be retried." and exit

2.  **Extract Task Info:**
    - Read original task JSON to get:
      - agent (required)
      - prompt (required)
      - retryCount (default to 0 if not present)
      - maxRetries (from original, or use $2, or default 3)
      - autoRetry (from original, or check if $3 or $2 contains "--auto")
      - errorMessage (from original task)
      - parentTaskId (original task's parentTaskId, or $1 if it doesn't have one)

3.  **Check Retry Limit:**
    - If retryCount >= maxRetries, report "Task $1 has reached max retries ($retryCount/$maxRetries). Cannot retry." and exit

4.  **Create Retry Task:**
    - Generate new Task ID: `task_<timestamp>`
    - Calculate retry attempt: NEW_RETRY_COUNT = retryCount + 1
    - Determine autoRetry flag:
      * If $2 or $3 contains "--auto", set to true
      * Otherwise, use value from original task (default false)
    - Create JSON file at `.gemini/agents/tasks/<New_Task_ID>.json`:
      ```json
      {
        "taskId": "<New_Task_ID>",
        "status": "pending",
        "agent": "<agent_from_original>",
        "prompt": "<prompt_from_original>",
        "planFile": ".gemini/agents/plans/<New_Task_ID>_plan.md",
        "logFile": ".gemini/agents/logs/<New_Task_ID>.log",
        "createdAt": "<ISO_TIMESTAMP>",
        "retryCount": <NEW_RETRY_COUNT>,
        "maxRetries": <maxRetries>,
        "autoRetry": <autoRetry_flag>,
        "parentTaskId": "<original_task_id_or_parent>",
        "retryHistory": [
          {
            "attempt": <NEW_RETRY_COUNT>,
            "timestamp": "<ISO_TIMESTAMP>",
            "error": "<errorMessage_from_original>",
            "retriedFrom": "$1"
          }
        ],
        "priority": 5
      }
      ```
    - If original task had retryHistory, merge it into the new task's retryHistory array

5.  **Create Plan File:**
    - Create `.gemini/agents/plans/<New_Task_ID>_plan.md`
    - Content:
      ```markdown
      # Retry Attempt <NEW_RETRY_COUNT>/<maxRetries>
      
      **Original Task:** $1
      **Previous Error:** <errorMessage_from_original>
      
      ## Task Prompt
      <prompt_from_original>
      
      ## Retry Strategy
      This is retry attempt <NEW_RETRY_COUNT> of <maxRetries>.
      Auto-retry: <enabled/disabled>
      ```

6.  **Update Original Task:**
    - Add a "retriedBy" field to original task JSON pointing to new task ID
    - Update "retriedAt" timestamp

7.  **Report:**
    - "Task <New_Task_ID> created as retry for $1 (attempt <NEW_RETRY_COUNT>/<maxRetries>)"
    - If autoRetry enabled: "Auto-retry enabled - will automatically retry on future failures"
    - "Use /agent:run or /agent:run-parallel to execute the retry"

**NOTES:**
- Retry tasks inherit agent and prompt from original
- Retry count increments with each attempt
- Auto-retry flag can be set during retry creation
- ParentTaskId links all retries to original task
- RetryHistory maintains full audit trail
