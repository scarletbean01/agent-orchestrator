"""Test script to verify prompt template loading."""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add .opencode to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".opencode"))

from cli.core.models import Task
from cli.core.repository import TaskRepository
from cli.core.executor import Executor

def test_prompt_template():
    """Test that prompt templates are loaded correctly."""
    
    # Load the test task
    repo = TaskRepository()
    task = repo.load("task_1764601210546")
    
    if not task:
        print("ERROR: Test task not found")
        return False
    
    print(f"✓ Loaded task: {task.taskId}")
    print(f"  Agent: {task.agent}")
    print(f"  Prompt: {task.prompt}")
    print()
    
    # Create executor and build command
    executor = Executor(repo)
    command = executor._build_command(task)
    
    print(f"✓ Built command:")
    print(f"  Command: {command[0]}")
    print(f"  Args count: {len(command) - 1}")
    print()
    
    # Find the prompt argument (should be after -i flag)
    try:
        i_index = command.index("-i")
        prompt_arg = command[i_index + 1]
        
        print(f"✓ Extracted prompt argument:")
        print(f"  Length: {len(prompt_arg)} characters")
        print()
        print("=" * 80)
        print("PROMPT CONTENT:")
        print("=" * 80)
        print(prompt_arg)
        print("=" * 80)
        print()
        
        # Verify key elements are present
        checks = {
            "Task ID present": f"Task ID: {task.taskId}" in prompt_arg,
            "User prompt present": task.prompt in prompt_arg,
            "Plan file present": task.planFile in prompt_arg,
            "Protocol section present": "PROTOCOL:" in prompt_arg,
            "Steps section present": "STEPS:" in prompt_arg,
            "Sentinel file instruction": ".done" in prompt_arg,
            "Error handling instruction": ".error" in prompt_arg,
        }
        
        print("VERIFICATION CHECKS:")
        all_passed = True
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        print()
        if all_passed:
            print("🎉 All checks passed! Prompt template system is working correctly.")
            return True
        else:
            print("❌ Some checks failed. Review the prompt content above.")
            return False
            
    except (ValueError, IndexError) as e:
        print(f"ERROR: Could not extract prompt from command: {e}")
        print(f"Command: {command}")
        return False

if __name__ == "__main__":
    success = test_prompt_template()
    sys.exit(0 if success else 1)

