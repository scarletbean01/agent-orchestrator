# OpenCode Agent Orchestrator

<p align="center">
  <strong>A high-performance, file-system-based agent orchestration framework</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#usage">Usage</a> •
  <a href="#agent-configuration">Agent Config</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## Overview

The Agent Orchestrator is a task queue management system for AI coding agents. It provides a simple, file-based approach to:

- 📋 **Queue tasks** for specialized AI agents
- 🔄 **Track progress** with real-time status monitoring
- ⚡ **Execute asynchronously** with parallel task support
- 🔌 **Plug in any agent** (OpenCode, Augment, Cursor, Claude, etc.)

## Features

| Feature | Description |
|---------|-------------|
| ⚡ **20-50x Faster** | High-performance Python CLI vs LLM-based commands |
| 🪟 **Cross-Platform** | Native support for Windows, macOS, and Linux |
| 📦 **Zero Dependencies** | Pure Python stdlib - no pip install required |
| 🎨 **Rich Output** | ANSI colors, formatted tables, status icons |
| 👀 **Watch Mode** | Real-time status monitoring with `--watch` |
| 🔄 **Parallel Execution** | Run multiple tasks concurrently |
| 🤖 **Daemon Mode** | Continuous execution with automatic task launching |
| ♻️ **Auto-Retry** | Automatic retry with exponential backoff |
| ⏱️ **Timeout Management** | Configurable timeouts with manual override |
| 🔌 **Agent Agnostic** | Configure any CLI tool via `agent-config.json` |
| 📝 **Prompt Templates** | Inject orchestration protocol into any agent |
| 🔧 **Debug Logging** | Switchable via `--debug` flag or `AGENT_DEBUG=1` |

## Quick Start

### Prerequisites

- Python 3.7+
- An AI coding agent CLI (e.g., [OpenCode](https://github.com/opencode-ai/opencode))

### Installation

```bash
# Clone the repository
git clone https://github.com/opencode/agent-orchestrator.git
cd agent-orchestrator

# Set up environment (add to your shell profile for persistence)
# Linux/macOS:
export PYTHONPATH=.orchestra-cli:$PYTHONPATH

# Windows PowerShell:
$env:PYTHONPATH = ".orchestra-cli;$env:PYTHONPATH"
```

### Your First Task

**Using OpenCode (default):**
```bash
# Create a task
python -m cli start coder "Write a hello world function in Python"

# Run the task
python -m cli run

# Watch progress
python -m cli status --watch
```

**Using Augment (with prompt templates):**
```bash
# Create a task for Augment
python -m cli start auggie "Create a FastAPI server with user authentication"

# Run the task
python -m cli run

# Monitor in real-time
python -m cli status --watch
```

> **Note:** Augment uses the prompt template system to receive full orchestration instructions. See [Agent Configuration](#agent-configuration) for details.

## Usage

### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `start` | Create a new task | `python -m cli start coder "Build a REST API"` |
| `run` | Execute pending tasks | `python -m cli run --parallel 3` |
| `daemon` | Run in daemon mode | `python -m cli daemon --max-concurrent 3 --interval 5` |
| `status` | View task status | `python -m cli status --watch` |
| `cancel` | Cancel a task | `python -m cli cancel task_123` |
| `retry` | Retry a failed task | `python -m cli retry task_123` |
| `clean` | Remove old tasks | `python -m cli clean completed` |
| `timeout` | Manage timeouts | `python -m cli timeout extend task_123 300` |
| `archive` | Archive old tasks | `python -m cli archive --dry-run` |
| `config` | Manage configuration | `python -m cli config show` |
| `deps` | Manage dependencies | `python -m cli deps graph` |
| `index` | Manage task index | `python -m cli index rebuild` |

### Global Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--debug`, `-d` | Enable debug logging | `python -m cli --debug run` |
| `--version` | Show version info | `python -m cli --version` |

### Common Workflows

**Sequential Execution:**
```bash
python -m cli start coder "Create user model"
python -m cli start coder "Add authentication"
python -m cli run           # Runs first task
python -m cli run           # Runs second task
```

**Parallel Execution:**
```bash
python -m cli start coder "Task 1"
python -m cli start coder "Task 2"
python -m cli start coder "Task 3"
python -m cli run --parallel 3   # Runs all 3 concurrently
```

**Daemon Mode (Continuous Execution):**
```bash
# Start daemon with auto-retry and continuous monitoring
python -m cli daemon --max-concurrent 3 --interval 5

# In another terminal, queue tasks and they'll execute automatically
python -m cli start coder "Task 1" --auto-retry
python -m cli start coder "Task 2" --timeout 300
python -m cli start auggie "Task 3"
# Daemon automatically picks up and executes tasks
```

**With Timeout and Auto-Retry:**
```bash
python -m cli start coder "Deploy service" --timeout 300 --auto-retry --max-retries 3
python -m cli run
```

**Using Augment (with Prompt Templates):**
```bash
# Create a task for Augment
python -m cli start auggie "Create a REST API for user management with CRUD operations"

# Run the task
python -m cli run

# Monitor progress in real-time
python -m cli status --watch

# Check the logs
cat .orchestra/logs/task_*.log
```

**Mixed Agent Workflow:**
```bash
# Use Augment for complex implementation
python -m cli start auggie "Implement authentication system with JWT"

# Use OpenCode for simpler tasks
python -m cli start coder "Add unit tests for auth module"

# Run both tasks in parallel
python -m cli run --parallel 2
```

**Production Workflow with Daemon:**
```bash
# Terminal 1: Start the daemon
python -m cli daemon --max-concurrent 5 --interval 3

# Terminal 2: Queue tasks as needed
python -m cli start coder "Fix bug #123" --auto-retry --max-retries 3
python -m cli start auggie "Implement feature X" --timeout 600
python -m cli start coder "Update documentation"

# Monitor progress
python -m cli status --watch

# The daemon automatically:
# - Picks up new tasks
# - Executes up to 5 concurrently
# - Retries failed tasks with auto-retry
# - Monitors task health every 3 seconds
```

### Daemon Mode

The daemon runs continuously, automatically executing tasks as they're queued.

**Basic Usage:**
```bash
# Start daemon (runs forever until stopped)
python -m cli daemon

# With custom settings
python -m cli daemon --max-concurrent 5 --interval 3
```

**Options:**
| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--max-concurrent` | `-c` | 3 | Maximum concurrent tasks |
| `--interval` | `-i` | 5 | Check interval in seconds |

**Features:**
- ✅ Automatic task launching when slots available
- ✅ Continuous state reconciliation
- ✅ Auto-retry for failed tasks with exponential backoff
- ✅ Graceful shutdown on Ctrl+C or SIGTERM
- ✅ Real-time status logging
- ✅ Error isolation (single failures don't crash daemon)

**Production Example:**
```bash
# Terminal 1: Run daemon in background
nohup python -m cli daemon --max-concurrent 10 --interval 2 > daemon.log 2>&1 &

# Terminal 2: Queue tasks
python -m cli start coder "Task 1" --auto-retry --max-retries 3
python -m cli start coder "Task 2" --timeout 600
python -m cli start auggie "Task 3"

# Monitor
python -m cli status --watch

# Stop daemon
pkill -f "python -m cli daemon"
```

**When to Use Daemon Mode:**
- 🔧 **CI/CD pipelines** - Continuous task processing
- 🏭 **Production environments** - Long-running orchestration
- 📊 **Batch processing** - Queue many tasks, let daemon handle them
- 🔄 **Auto-retry workflows** - Automatic failure recovery

**When to Use `run` Command:**
- 🧪 **Testing/development** - Manual control over execution
- 🎯 **Single tasks** - One-off executions
- 🔍 **Debugging** - Step-by-step task execution

### Slash Commands (Legacy)

If you're using OpenCode, slash commands are still supported:

```bash
/agent:start coder "Create a web server"
/agent:run
/agent:status
```

> **Note:** Slash commands call the Python CLI internally. Direct CLI usage is recommended for better performance.

## Agent Configuration

The orchestrator is **agent-agnostic**. Configure any CLI tool in `.orchestra-cli/agent-config.json`:

### Basic Configuration

```json
{
  "agents": {
    "coder": {
      "command": "opencode",
      "args": ["run", "{prompt}", "--agent", "coder"],
      "description": "Default OpenCode agent"
    },
    "auggie": {
      "command": "auggie",
      "args": ["-i", "{prompt}", "-w", ".", "--model", "sonnet4.5", "-p"],
      "description": "Augment CLI agent (Sonnet 4.5)",
      "promptTemplateFile": ".orchestra-cli/prompts/auggie.txt"
    },
    "cursor": {
      "command": "cursor",
      "args": ["--task", "{prompt}"],
      "description": "Cursor AI agent"
    }
  }
}
```

**Variable Substitution:**
- `{prompt}` - Full task prompt with completion instructions
- `{taskId}` - Unique task identifier
- `{agent}` - Agent name

**Usage:**
```bash
# Use different agents by name
python -m cli start coder "Build a feature"    # Uses opencode
python -m cli start auggie "Create REST API"   # Uses augment
python -m cli start cursor "Fix this bug"      # Uses cursor
```

### Prompt Templates

For agents that don't support the `.orchestra-cli/agent/` subagent system (like Augment, Cursor, etc.), you can use **prompt templates** to inject the full orchestration protocol into the prompt.

**Why Prompt Templates?**
- Agents like Augment don't have a built-in subagent configuration system
- Templates inject comprehensive instructions directly into the prompt
- Ensures agents follow the framework protocol (task IDs, sentinel files, error handling)

**Creating a Template:**

1. Create a template file in `.orchestra-cli/prompts/`:

```text
You are a coding agent.

Task ID: {taskId}
Task: {userPrompt}
Plan File: {planFile}

PROTOCOL:
1. Complete the task
2. Create .orchestra/tasks/{taskId}.done when finished
3. On failure, create .orchestra/tasks/{taskId}.error with error details
```

2. Reference it in `agent-config.json`:

```json
{
  "agents": {
    "myagent": {
      "command": "myagent",
      "args": ["--prompt", "{prompt}"],
      "promptTemplateFile": ".orchestra-cli/prompts/myagent.txt"
    }
  }
}
```

**Available Template Variables:**
- `{taskId}` - Unique task identifier
- `{userPrompt}` - User's original task description
- `{planFile}` - Path to plan file
- `{logFile}` - Path to log file
- `{agent}` - Agent name

**Included Templates:**
- `.orchestra-cli/prompts/auggie.txt` - Full protocol for Augment CLI
- `.orchestra-cli/prompts/default.txt` - Minimal template for generic agents

See [.orchestra-cli/prompts/README.md](.orchestra-cli/prompts/README.md) for detailed documentation.

### Debug Logging

Debug output can be enabled to troubleshoot command execution, prompt template loading, and platform-specific behavior.

**Enable via CLI flag:**
```bash
python -m cli --debug run                    # Enable for single command
python -m cli -d status --watch              # Short form
python -m cli --debug start auggie "Task"   # See command building
```

**Enable via environment variable:**
```bash
# Linux/macOS
export AGENT_DEBUG=1
python -m cli run

# Windows PowerShell
$env:AGENT_DEBUG = "1"
python -m cli run
```

**Debug output includes:**
- Command array construction
- Prompt template loading and variable substitution
- Platform-specific escaping (Windows newline handling)
- Process creation details
- Full argument list with character counts

**Log levels:**
| Level | Color | Description |
|-------|-------|-------------|
| DEBUG | Gray | Detailed info (only shown with `--debug`) |
| INFO | Green | Task lifecycle events |
| WARNING | Yellow | Recoverable errors |
| ERROR | Red | Critical failures |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
├─────────────────────────────────────────────────────────────┤
│  python -m cli ...  │  /agent:... (slash commands)          │
└──────────┬──────────┴──────────────┬────────────────────────┘
           │                         │
           ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Python CLI (.orchestra-cli/cli/)               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ models  │ │  repo   │ │executor │ │scheduler│           │
│  └─────────┘ └─────────┘ └────┬────┘ └─────────┘           │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────────┐                 │
│                    │  Prompt Templates    │                 │
│                    │  (.orchestra-cli/    │                 │
│                    │   prompts/)          │                 │
│                    └──────────────────────┘                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         Agent Execution (via agent-config.json)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ OpenCode │  │ Augment  │  │  Cursor  │  │   Any    │    │
│  │  (coder) │  │ (auggie) │  │          │  │   CLI    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            File System (.orchestra/)                        │
│  tasks/    │    plans/    │    logs/    │    workspace/     │
│  ├─ .json  │    ├─ .md    │    ├─ .log  │    ├─ output/    │
│  ├─ .done  │              │             │                   │
│  ├─ .error │              │             │                   │
│  └─ .pid   │              │             │                   │
└─────────────────────────────────────────────────────────────┘
```

**Components:**
- **Python CLI** - High-performance core (< 100ms response)
- **Daemon Mode** - Continuous execution with automatic task launching and retry
- **Retry Manager** - Centralized retry logic with exponential backoff
- **Prompt Templates** - Inject orchestration protocol into agent prompts
- **Agent Config** - Maps agent names to CLI commands with template support
- **LLM Commands** - Thin wrappers for slash command compatibility
- **Sub-Agents** - Specialized agents that perform actual work (OpenCode, Augment, etc.)
- **File Storage** - JSON-based task persistence with sentinel files (.done, .error, .pid)

## Task Lifecycle

```
┌─────────┐     ┌─────────┐     ┌──────────┐
│ pending │────▶│ running │────▶│ complete │
└─────────┘     └────┬────┘     └──────────┘
                     │
                     ├─────────▶ failed ──────▶ retry
                     │
                     └─────────▶ cancelled
```

## Directory Structure

```
.orchestra-cli/
├── cli/                    # Python CLI (high-performance core)
│   ├── agent.py            # CLI entry point with --debug flag
│   ├── commands/           # Command implementations
│   │   ├── start.py        # Task creation
│   │   ├── run.py          # Single/parallel execution
│   │   ├── daemon.py       # 🆕 Daemon mode with continuous execution
│   │   ├── status.py       # Status monitoring with auto-retry
│   │   ├── cancel.py       # Task cancellation
│   │   ├── retry.py        # Retry management
│   │   ├── clean.py        # Task cleanup
│   │   └── timeout_cmd.py  # Timeout management
│   ├── core/               # Business logic (models, repo, executor)
│   │   ├── models.py       # Task data models
│   │   ├── repository.py   # Task persistence
│   │   ├── reconciler.py   # State reconciliation
│   │   ├── scheduler.py    # Task scheduling with priority
│   │   ├── executor.py     # Process launching
│   │   ├── formatter.py    # Output formatting
│   │   └── retry_manager.py # 🆕 Centralized retry logic
│   └── utils/              # Utilities
│       ├── logger.py       # Centralized logging with debug toggle
│       ├── process.py      # Cross-platform process management
│       ├── paths.py        # Path constants
│       └── time_utils.py   # Duration formatting
├── command/                # LLM slash commands (thin wrappers)
├── agent/                  # Sub-agent definitions (for OpenCode)
├── prompts/                # Prompt templates for agents
│   ├── auggie.txt          # Augment CLI template
│   ├── default.txt         # Generic agent template
│   └── README.md           # Template documentation
├── agent-config.json       # Agent CLI configuration
└── scripts/                # Helper scripts and tests

.orchestra/
├── tasks/                  # Task JSON files + sentinel files
│   ├── task_*.json         # Task metadata
│   ├── task_*.done         # Completion markers
│   ├── task_*.error        # Error details
│   └── task_*.pid          # Process IDs
├── plans/                  # Task plan markdown files
├── logs/                   # Execution logs
└── workspace/              # Agent output directory
```

## Documentation

- **[AGENTS.md](AGENTS.md)** - Comprehensive framework documentation
- **[CONVENTIONS.md](CONVENTIONS.md)** - Coding conventions and style guide
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Upgrading from v1.0 to v2.0
- **[PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md)** - Prompt template system implementation guide
- **[.orchestra-cli/prompts/README.md](.orchestra-cli/prompts/README.md)** - Prompt template usage and best practices

## Testing

Run the integration test suite:

```bash
# Linux/macOS
.orchestra-cli/test-integration.sh

# Windows
python -m pytest .orchestra-cli/tests/
```

## Contributing

Contributions are welcome! Please read [CONVENTIONS.md](CONVENTIONS.md) before submitting PRs.

## License

MIT License - see [LICENSE](LICENSE) for details.
