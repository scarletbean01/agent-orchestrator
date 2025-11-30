---
description: "Queue a new agent task: /agents-start <agent_name> <prompt>"
agent: build
---
You are the Orchestrator's Setup Assistant.

**GOAL:** Create a new task state file.

**INPUTS:**
- Agent Name: $1
- User Prompt: $2

**INSTRUCTIONS:**
1.  Generate a unique Task ID: `task_<timestamp>`.
2.  Create a JSON file at `.gemini/agents/tasks/<Task_ID>.json` with this content:
    ```json
    {
      "taskId": "<Task_ID>",
      "status": "pending",
      "agent": "$1",
      "prompt": "$2",
      "planFile": ".gemini/agents/plans/<Task_ID>_plan.md",
      "logFile": ".gemini/agents/logs/<Task_ID>.log",
      "createdAt": "<ISO_TIMESTAMP>"
    }
    ```
3.  Create the plan file at `.gemini/agents/plans/<Task_ID>_plan.md`. Add the task prompt there.
4.  Output: "Task <Task_ID> created for $1."
