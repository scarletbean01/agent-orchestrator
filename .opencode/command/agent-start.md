---
description: "Queue a new agent task: /agent:start <agent_name> <prompt> [--max-retries N] [--auto-retry] [--priority N]"
agent: build
---
You are the Orchestrator's Setup Assistant.

**GOAL:** Create a new task state file with optional retry and priority settings.

**INPUTS:**
- Agent Name: $1
- User Prompt: $2
- Optional Flags: $3, $4, $5... (parse for --max-retries, --auto-retry, --priority)

**INSTRUCTIONS:**
1.  Generate a unique Task ID: `task_<timestamp>`.

2.  **Parse Optional Flags:**
    - Check all arguments for:
      * `--max-retries N` or `--max-retries=N` → extract N (default: 3)
      * `--auto-retry` → set autoRetry to true (default: false)
      * `--priority N` or `--priority=N` → extract N (default: 5)

3.  Create a JSON file at `.gemini/agents/tasks/<Task_ID>.json` with this content:
    ```json
    {
      "taskId": "<Task_ID>",
      "status": "pending",
      "agent": "$1",
      "prompt": "$2",
      "planFile": ".gemini/agents/plans/<Task_ID>_plan.md",
      "logFile": ".gemini/agents/logs/<Task_ID>.log",
      "createdAt": "<ISO_TIMESTAMP>",
      "retryCount": 0,
      "maxRetries": <parsed_or_default_3>,
      "autoRetry": <parsed_or_default_false>,
      "priority": <parsed_or_default_5>,
      "parentTaskId": null
    }
    ```

4.  Create the plan file at `.gemini/agents/plans/<Task_ID>_plan.md`. Add the task prompt there.

5.  **Output:**
    - "Task <Task_ID> created for $1."
    - If maxRetries != 3: "Max retries: <maxRetries>"
    - If autoRetry: "Auto-retry: enabled"
    - If priority != 5: "Priority: <priority>"

**NOTES:**
- All retry and priority fields are optional
- Defaults: maxRetries=3, autoRetry=false, priority=5
- Priority: 1-10 scale (higher = more important, for future scheduling)
