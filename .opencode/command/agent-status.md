---
description: "Show task queue status (v2.0 - faster Python CLI)"
agent: build
---
**⚠ DEPRECATION NOTICE**: This command now uses the new Python CLI for 20-50x faster performance.

Execute the status command:

```bash
cd /home/deplague/Projects/opencode-orchestrator && PYTHONPATH=.opencode:$PYTHONPATH python3 -m cli status
```

**Usage:**
- `python3 -m cli status` - Show status once
- `python3 -m cli status --watch` - Auto-refresh every 5 seconds
- `python3 -m cli status --watch --interval 2` - Custom refresh interval

**Note:** The new Python CLI provides:
- Instant status checks (<100ms vs 2-5s)
- Watch mode for monitoring
- Beautiful formatted output
- Reliable state reconciliation

If the Python command fails, report the error to the user.
