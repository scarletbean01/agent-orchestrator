---
description: "Queue a new agent task (v2.0 - faster Python CLI)"
agent: build
---
**⚠ DEPRECATION NOTICE**: This command now uses the new Python CLI for instant task creation.

Execute the start command with all arguments:

```bash
cd /home/deplague/Projects/opencode-orchestrator && PYTHONPATH=.opencode:$PYTHONPATH python3 -m cli start "$@"
```

**Usage Examples:**
- `python3 -m cli start coder "Create a web server"`
- `python3 -m cli start coder "Deploy app" --timeout 600 --auto-retry`
- `python3 -m cli start coder "Process data" --priority 8 --max-retries 5`

**Options:**
- `--max-retries N` - Maximum retry attempts (default: 3)
- `--auto-retry` - Enable automatic retries on failure
- `--priority N` - Task priority 1-10 (default: 5, higher = more important)
- `--timeout N` - Timeout in seconds (no default)

**Note:** The new Python CLI provides:
- Instant task creation (<50ms vs 1-2s)
- Proper argument parsing
- Input validation

If the Python command fails, report the error to the user.
