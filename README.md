# OpenCode Agent Orchestrator

The OpenCode Agent Orchestrator is a file-system-based agent orchestration framework built on top of OpenCode's custom command and agent system. It provides a simple, file-based approach to delegating work to specialized agents, tracking their progress, and managing asynchronous task execution.

## Features

*   **Task Queue Management:** A robust task queue management system for AI agents.
*   **High-Performance CLI:** A high-performance Python CLI for managing tasks, achieving 20-50x performance improvement over LLM-based commands.
*   **Rich Output:** ANSI colors, formatted tables, and status icons for a better user experience.
*   **Soft Migration:** Both LLM and Python CLI work during the transition, ensuring full backward compatibility.
*   **Zero Dependencies:** The Python CLI is built with pure Python stdlib, requiring no external dependencies.
*   **Cross-Platform:** Supports Linux, macOS, and Windows.
*   **Watch Mode:** Real-time status monitoring with the `--watch` flag.
*   **Parallel Execution:** Run multiple tasks concurrently.
*   **Auto-Retry:** Automatically retry failed tasks.
*   **Timeout Management:** Manage task timeouts with manual control.

## Getting Started

### Prerequisites

*   Python 3.7+

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/opencode/agent-orchestrator.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd agent-orchestrator
    ```
3.  Set up the environment:
    ```bash
    export PYTHONPATH=.opencode:$PYTHONPATH
    ```

## Usage

### Python CLI

The recommended way to use the orchestrator is through the Python CLI.

*   **Status:**
    ```bash
    python3 -m cli status --watch
    ```
*   **Start:**
    ```bash
    python3 -m cli start coder "Create a web server" --timeout 300
    ```
*   **Run:**
    ```bash
    python3 -m cli run --parallel 3
    ```

### Slash Commands

You can also use the slash commands, which call the Python CLI internally.

*   **Status:**
    ```bash
    /agent:status
    ```
*   **Start:**
    ```bash
    /agent:start coder "Create a web server"
    ```
*   **Run:**
    ```bash
    /agent:run
    ```

## Integration Testing

To validate your setup and cross-platform compatibility, use the integration test script:

```bash
.opencode/test-integration.sh
```

This script tests task creation, status, cancellation, cleaning, timeouts, agent config switching (including the "cursor" agent), and more. For full cross-platform validation, run this script and inspect logs on both Linux/macOS and Windows environments. Defensive logging is used for process management and agent command invocation.

## Architecture

The v2.0 system uses a 3-layer hybrid architecture:

1.  **Python CLI (`.opencode/cli/`):** High-performance core.
2.  **LLM Commands (`.opencode/command/`):** Thin wrappers for slash command compatibility.
3.  **LLM Sub-Agents (`.opencode/agent/`):** Specialized agents for actual work.

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONVENTIONS.md) before getting started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
