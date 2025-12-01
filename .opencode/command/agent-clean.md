---
description: "Clean up tasks: /agent:clean [completed|failed|cancelled|all|task_id]"
agent: build
---
You are the Task Cleanup Manager.

**⚠️ DEPRECATION NOTICE:** This LLM-based command has been replaced by a Python CLI for 20-50x performance improvement.

**GOAL:** Execute the Python CLI to remove old task files.

**INPUT:** Filter type: $1 (optional, defaults to "completed")

**STEPS:**
1.  **Execute Python CLI:**
    ```bash
    cd /home/deplague/Projects/opencode-orchestrator && PYTHONPATH=.opencode:$PYTHONPATH python3 -m cli clean ${1:-completed} -y
    ```

2.  **Report:** The Python CLI will output the result. Simply pass through the output to the user.

**NOTES:**
- The Python CLI handles all cleanup logic (filtering, safety checks, file deletion)
- Valid filters: completed, failed, cancelled, all, task_<id>
- The `-y` flag skips confirmation prompts
- This LLM wrapper will be removed in a future version

**GOAL:** Remove old task files based on filter criteria.

**INPUT:** Filter type: $1 (optional, defaults to "completed")

**FILTERS:**
- `completed` - Remove only completed tasks
- `failed` - Remove only failed tasks  
- `cancelled` - Remove only cancelled tasks
- `all` - Remove all non-running and non-pending tasks
- `task_XXXXX` - Remove specific task by ID (if it starts with "task_")

**STEPS:**
1.  **Determine Filter:** 
    - If $1 is empty, use "completed"
    - If $1 starts with "task_", treat as specific task ID

2.  **Find Matching Tasks:**
    - Scan `.gemini/agents/tasks/*.json`
    - Parse each JSON file to check status
    - Select tasks matching the filter criteria
    - **SAFETY:** NEVER delete tasks with status "running" or "pending"

3.  **Delete Task Artifacts:**
    - For each matching task with Task_ID:
      a. Remove `.gemini/agents/tasks/<Task_ID>.json`
      b. Remove `.gemini/agents/plans/<Task_ID>_plan.md` (if exists)
      c. Remove `.gemini/agents/logs/<Task_ID>.log` (if exists)
      d. Remove any sentinel files: `.gemini/agents/tasks/<Task_ID>.done`, `.error`, `.cancelled` (if exist)

4.  **Report:** 
    - Count of tasks removed
    - List of removed task IDs
    - Example: "Cleaned up 3 completed tasks: task_123, task_456, task_789"
    - If no tasks match: "No tasks found matching filter: $1"

**Safety:** If more than 10 tasks match the filter, list them and ask for confirmation before deleting.
