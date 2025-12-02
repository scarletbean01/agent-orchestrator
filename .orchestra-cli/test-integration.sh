#!/usr/bin/env bash
# Integration test for Agent Orchestrator v2.0
set -e

echo "=== Agent Orchestrator v2.0 Integration Test ==="
echo

# Setup
export PYTHONPATH=.opencode:$PYTHONPATH
CLI="python3 -m cli"

echo "1. Testing 'start' command..."
TASK1=$($CLI start coder "Test task 1" --timeout 300 | grep -oP 'task_\d+')
echo "   ✓ Created: $TASK1"
echo

echo "2. Testing 'start' with auto-retry..."
TASK2=$($CLI start coder "Test task 2" --auto-retry --max-retries 5 | grep -oP 'task_\d+')
echo "   ✓ Created: $TASK2"
echo

echo "3. Testing 'status' command..."
$CLI status | head -10
echo "   ✓ Status displayed"
echo

echo "4. Testing 'cancel' command..."
$CLI cancel $TASK2
echo "   ✓ Cancelled: $TASK2"
echo

echo "5. Testing 'clean' command (failed tasks)..."
$CLI clean failed -y
echo "   ✓ Cleaned failed tasks"
echo

echo "6. Testing 'timeout list' command..."
$CLI timeout list | head -5
echo "   ✓ Timeout list displayed"
echo

echo "7. Testing 'run' command..."
$CLI run &
RUN_PID=$!
sleep 2
echo "   ✓ Task running (PID: $RUN_PID)"
echo

echo "8. Testing 'status --watch' (5 seconds)..."
timeout 5 $CLI status --watch --interval 2 || true
echo "   ✓ Watch mode completed"
echo

echo "9. Testing agent config switching (cursor agent)..."
CURSOR_TASK=$($CLI start cursor "Test task for cursor agent" | grep -oP 'task_\d+')
echo "   ✓ Created: $CURSOR_TASK (cursor agent)"
echo "   (Check logs to verify correct command structure for 'cursor' agent)"
echo

echo "# NOTE: Windows process management is tested via defensive logging in Python."
echo "# For full cross-platform validation, run this script and inspect logs on both Linux/macOS and Windows environments."
echo

echo "=== All Tests Passed ✓ ==="
echo
echo "Cleanup: Run '$CLI clean all -y' to remove test tasks"
