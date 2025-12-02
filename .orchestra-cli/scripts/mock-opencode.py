#!/usr/bin/env python3
"""
Mock OpenCode CLI for testing the agent orchestrator.
This simulates the 'opencode run' command behavior.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime


def main():
    """Mock opencode run command."""
    # Parse args
    if len(sys.argv) < 2:
        print("Usage: mock-opencode.py run <prompt> [--agent <agent>]")
        sys.exit(1)

    command = sys.argv[1]
    if command != "run":
        print(f"Unknown command: {command}")
        sys.exit(1)

    # Extract prompt (may contain task ID)
    prompt = sys.argv[2] if len(sys.argv) > 2 else "No prompt provided"

    # Extract task ID from prompt
    task_id = None
    if "Your Task ID is" in prompt:
        try:
            task_id = prompt.split("Your Task ID is ")[1].split(".")[0].strip()
        except:
            pass

    print(f"[Mock OpenCode] Starting task: {task_id or 'unknown'}")
    print(f"[Mock OpenCode] Prompt: {prompt[:100]}...")

    # Simulate some work
    print("[Mock OpenCode] Analyzing project structure...")
    time.sleep(2)

    print("[Mock OpenCode] Generating code...")
    time.sleep(2)

    print("[Mock OpenCode] Writing files...")
    time.sleep(1)

    # Create completion sentinel file
    if task_id:
        sentinel_path = Path(f".orchestra/tasks/{task_id}.done")
        sentinel_path.parent.mkdir(parents=True, exist_ok=True)

        with open(sentinel_path, "w") as f:
            json.dump(
                {
                    "completedAt": datetime.now().isoformat(),
                    "message": "Task completed successfully (mock)",
                },
                f,
                indent=2,
            )

        print(f"[Mock OpenCode] ✓ Task completed successfully")
        print(f"[Mock OpenCode] Created sentinel: {sentinel_path}")
    else:
        print("[Mock OpenCode] Warning: No task ID found, cannot create sentinel file")

    sys.exit(0)


if __name__ == "__main__":
    main()
