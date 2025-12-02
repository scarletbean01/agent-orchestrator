# Prompt Template System - Implementation Summary

## Overview

The prompt template system allows you to inject comprehensive orchestration protocols into agents that don't support the `.opencode/agent/` subagent system (like Augment, Cursor, etc.).

## What Was Implemented

### 1. Template Files Created

**`.orchestra-cli/prompts/auggie.txt`**
- Full orchestration protocol for Augment CLI
- Includes all framework requirements:
  - Task ID extraction
  - Plan file updates
  - Workspace management (`.orchestra/workspace/`)
  - Convention checking (PROJECT.md, CONVENTIONS.md)
  - Sentinel file creation (`.done`, `.error`)
  - Comprehensive error handling

**`.orchestra-cli/prompts/default.txt`**
- Minimal template for generic agents
- Basic completion signaling
- Fallback option for new agents

**`.orchestra-cli/prompts/README.md`**
- Complete documentation
- Usage examples
- Best practices
- Troubleshooting guide

### 2. Executor Enhancements

**Modified: `.orchestra-cli/cli/core/executor.py`**

Added three new methods:

1. **`_build_basic_prompt(task)`**
   - Creates the simple prompt (original behavior)
   - Used as fallback when no template is configured

2. **`_load_prompt_template(template_file, task)`**
   - Loads template from file
   - Handles file not found errors gracefully
   - Returns basic prompt on failure

3. **`_format_prompt_template(template, task)`**
   - Performs variable substitution
   - Supports: `{taskId}`, `{userPrompt}`, `{planFile}`, `{logFile}`, `{agent}`
   - Handles missing variables gracefully

**Updated: `_build_command(task)`**
- Now checks for `promptTemplateFile` in agent config
- Falls back to `promptTemplate` (inline)
- Falls back to basic prompt if neither exists
- Maintains full backward compatibility

### 3. Configuration Update

**Modified: `.orchestra-cli/agent-config.json`**

Added `promptTemplateFile` to auggie agent:

```json
{
  "agents": {
    "auggie": {
      "command": "auggie",
      "args": ["-i", "{prompt}", "-w", ".", "--model", "sonnet4.5", "-p"],
      "description": "Augment CLI agent (Sonnet 4.5)",
      "promptTemplateFile": ".orchestra-cli/prompts/auggie.txt"
    }
  }
}
```

### 4. Testing Infrastructure

**Created: `.orchestra-cli/scripts/test-prompt-template.py`**
- Verifies template loading
- Checks variable substitution
- Validates protocol elements
- Displays full prompt for inspection

## How It Works

### Flow Diagram

```
User creates task
    ↓
python -m cli start auggie "Build feature X"
    ↓
Task JSON created with taskId, prompt, planFile, etc.
    ↓
python -m cli run
    ↓
Executor._build_command(task)
    ↓
Checks agent-config.json for "auggie"
    ↓
Finds promptTemplateFile: ".orchestra-cli/prompts/auggie.txt"
    ↓
Loads template file
    ↓
Substitutes variables:
  {taskId} → task_1764601210546
  {userPrompt} → Build feature X
  {planFile} → .orchestra/plans/task_XXX_plan.md
  {logFile} → .orchestra/logs/task_XXX.log
    ↓
Builds command: auggie -i "{full_prompt}" -w . --model sonnet4.5 -p
    ↓
Launches process
    ↓
Augment receives full protocol in prompt
    ↓
Augment creates .done or .error file when finished
    ↓
python -m cli status (reconciliation)
    ↓
Task marked as complete or failed
```

## Usage Examples

### Using Augment with Full Protocol

```bash
# Create a task for Augment
python -m cli start auggie "Create a REST API for user management"

# Run the task
python -m cli run

# Monitor progress
python -m cli status --watch
```

The auggie agent will receive a comprehensive prompt that includes:
- Task identification
- Plan file location
- Workspace instructions
- Convention checking requirements
- Completion signaling protocol
- Error handling instructions

### Adding a New Agent

**Step 1:** Create template file `.orchestra-cli/prompts/cursor.txt`

```
You are a coding agent.

Task ID: {taskId}
Task: {userPrompt}

Complete the task and create .orchestra/tasks/{taskId}.done when finished.
```

**Step 2:** Add to `agent-config.json`

```json
{
  "agents": {
    "cursor": {
      "command": "cursor",
      "args": ["--task", "{prompt}"],
      "promptTemplateFile": ".orchestra-cli/prompts/cursor.txt"
    }
  }
}
```

**Step 3:** Use it

```bash
python -m cli start cursor "Implement feature Y"
python -m cli run
```

## Key Benefits

1. **Agent Decoupling**: Use any CLI tool without modifying code
2. **Protocol Injection**: Full orchestration protocol in every prompt
3. **Maintainability**: Templates are separate files, easy to update
4. **Flexibility**: Supports both file-based and inline templates
5. **Backward Compatibility**: Existing agents (coder) continue to work
6. **Graceful Degradation**: Falls back to basic prompt if template fails

## Testing

Verify the implementation:

```bash
# Create a test task
python -m cli start auggie "Test task"

# Run the test script
python .orchestra-cli/scripts/test-prompt-template.py
```

Expected output:
```
✓ Loaded task: task_XXXXX
✓ Built command
✓ Extracted prompt argument
  Length: 2416 characters

VERIFICATION CHECKS:
  ✓ Task ID present
  ✓ User prompt present
  ✓ Plan file present
  ✓ Protocol section present
  ✓ Steps section present
  ✓ Sentinel file instruction
  ✓ Error handling instruction

🎉 All checks passed!
```

## Template Variables Reference

All templates support these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{taskId}` | Unique task identifier | `task_1764601210546` |
| `{userPrompt}` | User's original task description | `Create a REST API` |
| `{planFile}` | Path to plan file | `.orchestra/plans/task_XXX_plan.md` |
| `{logFile}` | Path to log file | `.orchestra/logs/task_XXX.log` |
| `{agent}` | Agent name | `auggie`, `coder`, etc. |

## Configuration Options

### Option 1: Template File (Recommended)

```json
{
  "agents": {
    "myagent":     {
      "command": "myagent",
      "args": ["--prompt", "{prompt}"],
      "promptTemplateFile": ".orchestra-cli/prompts/myagent.txt"
    }
  }
}
```

### Option 2: Inline Template

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

### Option 3: No Template (Basic Prompt)

```json
{
  "agents": {
    "myagent": {
      "command": "myagent",
      "args": ["--prompt", "{prompt}"]
    }
  }
}
```

Falls back to: `"Your Task ID is {taskId}. Task: {userPrompt}. Signal completion by creating .orchestra/tasks/{taskId}.done"`

## Next Steps

1. **Test with real Augment tasks**: Create actual coding tasks and verify completion
2. **Add more templates**: Create templates for other agents (Cursor, etc.)
3. **Enhance templates**: Add more detailed instructions based on experience
4. **Monitor logs**: Check `.orchestra/logs/` for agent behavior
5. **Iterate**: Refine templates based on what works and what doesn't

## Troubleshooting

### Template not loading?
- Check the file path in `agent-config.json` is correct
- Ensure the template file exists and is readable
- Check the debug output when running tasks: `DEBUG: Loaded prompt template from ...`

### Variables not substituting?
- Ensure you're using the correct variable names (case-sensitive)
- Check for typos in `{variable}` placeholders
- Review the executor debug logs

### Agent not completing tasks?
- Verify the template includes `.done` file creation instructions
- Check the agent's log file for errors: `cat .orchestra/logs/task_*.log`
- Ensure the agent has permission to create files in `.orchestra/tasks/`

### Prompt too long?
- Some agents have prompt length limits
- Consider creating a shorter template
- Use inline template with minimal instructions

## Architecture Integration

The prompt template system integrates seamlessly with the orchestrator:

```
┌─────────────────────────────────────┐
│         Task Creation               │
│  python -m cli start auggie "..."   │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│      Task Repository                │
│  Saves task JSON with metadata      │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│         Executor                    │
│  1. Loads agent config              │
│  2. Finds promptTemplateFile        │
│  3. Loads template                  │
│  4. Substitutes variables           │
│  5. Builds command                  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│      Agent Execution                │
│  Receives full protocol in prompt   │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│    Completion Signaling             │
│  Creates .done or .error file       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│      Reconciliation                 │
│  Updates task status                │
└─────────────────────────────────────┘
```

## Files Modified/Created

### Created
- `.orchestra-cli/prompts/auggie.txt` (60 lines)
- `.orchestra-cli/prompts/default.txt` (24 lines)
- `.orchestra-cli/prompts/README.md` (150 lines)
- `.orchestra-cli/scripts/test-prompt-template.py` (90 lines)

### Modified
- `.orchestra-cli/cli/core/executor.py` (+108 lines)
- `.orchestra-cli/agent-config.json` (+1 line)
- `README.md` (+130 lines)

## Version History

- **v2.1** - Prompt template system implementation (2025-12-01)
- **v2.0** - Python CLI migration
- **v1.0** - Initial LLM-based orchestrator
