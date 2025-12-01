#!/bin/bash

# run-with-timeout.sh
# Usage: ./run-with-timeout.sh <TASK_ID> <TIMEOUT> <AGENT_NAME> <PROMPT>

TASK_ID="$1"
TIMEOUT="$2"
AGENT_NAME="$3"
PROMPT="$4"

# Validate inputs
if [ -z "$TASK_ID" ] || [ -z "$AGENT_NAME" ] || [ -z "$PROMPT" ]; then
  echo "Error: Missing required arguments"
  echo "Usage: $0 <TASK_ID> <TIMEOUT> <AGENT_NAME> <PROMPT>"
  exit 1
fi

# Construct the command
CMD="opencode run \"Your Task ID is $TASK_ID. Task: $PROMPT. Signal completion by creating .gemini/agents/tasks/$TASK_ID.done\" --agent $AGENT_NAME"

# Execute with or without timeout
if [ -n "$TIMEOUT" ] && [ "$TIMEOUT" != "null" ]; then
  # Use GNU timeout with 5s grace period for SIGKILL
  # Preserves status unless timeout occurs (124)
  timeout -k 5s "${TIMEOUT}s" $CMD
else
  # No timeout - run normally
  $CMD
fi

# Capture exit code
EXIT_CODE=$?

# Record exit code
echo "$EXIT_CODE" > ".gemini/agents/tasks/$TASK_ID.exitcode"

# If exit code 124, create timeout sentinel
if [ $EXIT_CODE -eq 124 ]; then
  TIMESTAMP=$(date -Iseconds)
  echo "{\"timeout\": $TIMEOUT, \"timestamp\": \"$TIMESTAMP\"}" > ".gemini/agents/tasks/$TASK_ID.timeout"
  echo "Task timed out after ${TIMEOUT}s (Exit Code: 124)"
fi

exit $EXIT_CODE
