#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Agent System Testing
"""

import sys
import os
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.agent_manager import AgentManager
from agents.file_saver import get_file_saver


def test_agent_manager():
    """Test AgentManager initialization."""
    print("=" * 70)
    print("TEST 1: AgentManager Initialization")
    print("=" * 70)

    manager = AgentManager()
    agents = manager.list_agents()

    print(f"\n[OK] Registered agents: {len(agents)}")

    for agent in agents:
        print(f"  - {agent['name']}")
        print(f"    {agent['description']}")
        print(f"    Capabilities: {len(agent['capabilities'])}")

    return manager


def test_can_handle(manager):
    """Test task recognition."""
    print("\n" + "=" * 70)
    print("TEST 2: Task Recognition")
    print("=" * 70)

    test_tasks = [
        ("Create landing page for coffee shop", "Web Developer"),
        ("Write Python script for parsing", "Programmer"),
        ("Analyze data from CSV", "Data Analyst"),
        ("Create mobile app design", "Designer"),
        ("Create Docker file for project", "DevOps"),
    ]

    for task, expected_agent in test_tasks:
        agent = manager.find_suitable_agent(task)
        if agent:
            status = "[OK]" if agent.name == expected_agent else "[WARN]"
            print(f"{status} '{task[:40]}...' -> {agent.name}")
        else:
            print(f"[FAIL] '{task[:40]}...' -> Agent not found")


def test_execute_tasks(manager):
    """Test task execution."""
    print("\n" + "=" * 70)
    print("TEST 3: Task Execution (without AI)")
    print("=" * 70)

    test_tasks = [
        "Create landing page for coffee shop",
        "Write Python script for parsing",
        "Create color scheme for website",
        "Create Docker file for project",
    ]

    for task in test_tasks:
        print(f"\n[Task] {task}")
        result = manager.execute_task(task)

        if result.get("status") == "success":
            print(f"  [OK] Status: {result.get('type', 'unknown')}")
            print(f"  [Files] Created: {len(result.get('files', {}))}")

            for filename in list(result.get("files", {}).keys())[:3]:
                print(f"     - {filename}")
        else:
            print(f"  [FAIL] Error: {result.get('message', 'Unknown error')}")


def test_file_saver():
    """Test FileSaver."""
    print("\n" + "=" * 70)
    print("TEST 4: File Saving to Disk")
    print("=" * 70)

    file_saver = get_file_saver()

    test_files = {
        "test.html": "<!DOCTYPE html><html><body><h1>Test</h1></body></html>",
        "test.css": "body { margin: 0; padding: 0; }",
        "test.js": 'console.log("Hello from JARVIS!");'
    }

    result = file_saver.save_files(
        files=test_files,
        project_name="Test Project",
        agent_name="Test Agent"
    )

    if result.get("status") == "success":
        print(f"[OK] Project created: {result.get('project_dir')}")
        print(f"[Files] Saved: {result.get('files_saved')}")

        for file_info in result.get("files", []):
            print(f"  - {file_info['filename']} ({file_info['size']} bytes)")
    else:
        print(f"[FAIL] Error: {result.get('message')}")


def test_voice_commands(manager):
    """Test voice commands."""
    print("\n" + "=" * 70)
    print("TEST 5: Voice Commands")
    print("=" * 70)

    commands = [
        "what agents are available",
        "task history",
        "Web Developer agent capabilities",
        "Programmer agent status"
    ]

    for command in commands:
        print(f"\n[Command] '{command}'")

        if "what agents" in command:
            agents = manager.list_agents()
            print(f"  [OK] Found agents: {len(agents)}")
            for agent in agents[:3]:
                print(f"     - {agent['name']}")

        elif "task history" in command:
            history = manager.get_task_history()
            print(f"  [OK] Tasks in history: {len(history)}")

        elif "capabilities" in command:
            agent_name = "Web Developer"
            agent = manager.get_agent(agent_name)
            if agent:
                print(f"  [OK] {agent_name} capabilities:")
                for cap in agent.capabilities[:3]:
                    print(f"     - {cap}")

        elif "status" in command:
            agent_name = "Programmer"
            agent = manager.get_agent(agent_name)
            if agent:
                status = agent.get_status()
                print(f"  [OK] {agent_name} status:")
                print(f"     - Tasks completed: {status['tasks_completed']}")


def main():
    """Main testing function."""
    print("\n" + "=" * 70)
    print("JARVIS AGENT SYSTEM - TESTING")
    print("=" * 70 + "\n")

    try:
        manager = test_agent_manager()
        test_can_handle(manager)
        test_execute_tasks(manager)
        test_file_saver()
        test_voice_commands(manager)

        print("\n" + "=" * 70)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] Testing error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
