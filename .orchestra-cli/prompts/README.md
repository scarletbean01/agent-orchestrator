# Prompt Templates

This directory contains prompt templates for different agents in the orchestrator framework.

## Overview

Prompt templates allow you to define comprehensive instructions for agents that don't support the `.orchestra-cli/agent/` subagent system (like Augment, Cursor, etc.). The template system injects the full orchestration protocol into the prompt that gets passed to the agent.

## How It Works

1. **Template Files**: Create a `.txt` file in this directory with your prompt template
2. **Variable Substitution**: Use `{variable}` placeholders that get replaced with task data
3. **Configuration**: Reference the template in `.opencode/agent-config.json`

## Available Variables

Templates support the following variables:

- `{taskId}` - Unique task identifier (e.g., `task_1764601210546`)
- `{userPrompt}` - The user's original task description
- `{planFile}` - Path to the plan file (e.g., `.orchestra/plans/task_XXX_plan.md`)
- `{logFile}` - Path to the log file (e.g., `.orchestra/logs/task_XXX.log`)
- `{agent}` - Agent name (e.g., `auggie`, `coder`)

## Usage

### Option 1: Template File (Recommended)

**Step 1:** Create a template file (e.g., `auggie.txt`)

```
You are a coding agent.

Task ID: {taskId}
Task: {userPrompt}

Instructions:
1. Complete the task
2. Create .orchestra/tasks/{taskId}.done when finished
```

**Step 2:** Reference it in `agent-config.json`

```json
{
  "agents": {
    "auggie": {
      "command": "auggie",
      "args": ["-i", "{prompt}", "-w", "."],
      "promptTemplateFile": ".orchestra-cli/prompts/auggie.txt"
    }
  }
}
```

### Option 2: Inline Template

You can also define templates inline in `agent-config.json`:

```json
{
  "agents": {
    "myagent": {
      "command": "myagent",
      "args": ["--prompt", "{prompt}"],
      "promptTemplate": "Task: {userPrompt}\nCreate {taskId}.done when done."
    }
  }
}
```

## Template Best Practices

### Essential Elements

Every template should include:

1. **Task identification**: Include `{taskId}` so the agent knows which task it's working on
2. **Completion signal**: Instruct the agent to create `.orchestra/tasks/{taskId}.done`
3. **Error handling**: Instruct the agent to create `.orchestra/tasks/{taskId}.error` on failure
4. **Clear instructions**: Explain the protocol and expectations

### Example Structure

```
You are a [ROLE] agent.

**YOUR TASK:**
Task ID: {taskId}
Task: {userPrompt}

**PROTOCOL:**
1. [Step 1]
2. [Step 2]
3. Create .orchestra/tasks/{taskId}.done when finished

**ON FAILURE:**
Create .orchestra/tasks/{taskId}.error with error details
```

## Included Templates

- **`auggie.txt`**: Full protocol for Augment CLI agent
  - Includes convention checking (PROJECT.md, CONVENTIONS.md)
  - Plan file updates
  - Workspace management
  - Comprehensive error handling

- **`default.txt`**: Minimal template for generic agents
  - Basic task execution
  - Simple completion signaling

## Testing

To verify your template is working:

```bash
# Create a test task
python -m cli start myagent "Test task"

# Run the test script
python .orchestra-cli/scripts/test-prompt-template.py
```

The test script will show you the exact prompt that gets sent to the agent.

## Troubleshooting

**Template not loading?**
- Check the file path in `agent-config.json` is correct
- Ensure the template file exists and is readable
- Check the debug output when running tasks

**Variables not substituting?**
- Ensure you're using the correct variable names (case-sensitive)
- Check for typos in `{variable}` placeholders
- Review the executor debug logs

**Agent not completing tasks?**
- Verify the template includes `.done` file creation instructions
- Check the agent's log file for errors
- Ensure the agent has permission to create files in `.orchestra/tasks/`

