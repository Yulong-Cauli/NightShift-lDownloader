#!/usr/bin/env python3
"""
Comprehensive demo showing all features of NightShift-lDownloader
"""

import os
import sys
from datetime import datetime

# Ensure we can import from the current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_manager import DownloadManager, TaskType


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    print_section("NightShift-lDownloader - Complete Feature Demo")
    
    # Initialize the manager
    print("\n1. Initializing Download Manager...")
    manager = DownloadManager(
        tasks_file="demo_tasks.json",
        download_dir="demo_downloads"
    )
    print("   ✓ Manager initialized")
    print(f"   - Tasks file: demo_tasks.json")
    print(f"   - Download directory: demo_downloads/")
    
    # Check time window
    print_section("2. Time Window Check")
    current_time = datetime.now().strftime("%H:%M:%S")
    is_within = manager.is_within_window()
    print(f"   Current time: {current_time}")
    print(f"   Time window: 03:00:00 - 08:00:00")
    print(f"   Status: {'✓ WITHIN WINDOW' if is_within else '✗ OUTSIDE WINDOW'}")
    
    # Add various types of tasks
    print_section("3. Adding Tasks")
    
    print("\n   A. Video Download Tasks")
    print("   " + "-" * 50)
    
    # YouTube video
    task1 = manager.add_task(
        TaskType.VIDEO_DOWNLOAD.value,
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
    )
    print(f"   ✓ Added YouTube video download: {task1}")
    
    # X/Twitter video
    task2 = manager.add_task(
        TaskType.VIDEO_DOWNLOAD.value,
        {
            "url": "https://x.com/example/status/123456789",
        }
    )
    print(f"   ✓ Added X/Twitter video download: {task2}")
    
    print("\n   B. Telegram Video Tasks")
    print("   " + "-" * 50)
    
    task3 = manager.add_task(
        TaskType.TELEGRAM_VIDEO.value,
        {
            "url": "https://t.me/channel_name/456",
            # Note: Requires Telegram API credentials in environment or here
        }
    )
    print(f"   ✓ Added Telegram video download: {task3}")
    print("   Note: Requires TELEGRAM_API_ID and TELEGRAM_API_HASH")
    
    print("\n   C. Library Installation Tasks")
    print("   " + "-" * 50)
    
    # Simple shell command
    task4 = manager.add_task(
        TaskType.LIBRARY_INSTALL.value,
        {
            "command": "pip install requests"
        }
    )
    print(f"   ✓ Added library installation: {task4}")
    
    # Docker command
    task5 = manager.add_task(
        TaskType.LIBRARY_INSTALL.value,
        {
            "container_name": "my_python_container",
            "command": "pip install torch torchvision"
        }
    )
    print(f"   ✓ Added Docker library installation: {task5}")
    
    # Task persistence
    print_section("4. Task Persistence")
    print(f"\n   Total tasks added: {len(manager.tasks)}")
    print("   Tasks are saved to: demo_tasks.json")
    print("\n   Task Summary:")
    
    task_types = {}
    for task in manager.tasks:
        task_type = task["type"]
        task_types[task_type] = task_types.get(task_type, 0) + 1
    
    for task_type, count in task_types.items():
        print(f"   - {task_type}: {count}")
    
    # Show task details
    print_section("5. Task Details")
    for i, task in enumerate(manager.tasks, 1):
        print(f"\n   Task {i}:")
        print(f"   - ID: {task['id']}")
        print(f"   - Type: {task['type']}")
        print(f"   - Status: {task['status']}")
        print(f"   - Created: {task['created_at']}")
        
        if task['type'] == TaskType.VIDEO_DOWNLOAD.value:
            print(f"   - URL: {task['payload']['url']}")
        elif task['type'] == TaskType.TELEGRAM_VIDEO.value:
            print(f"   - URL: {task['payload']['url']}")
        elif task['type'] == TaskType.LIBRARY_INSTALL.value:
            if 'container_name' in task['payload']:
                print(f"   - Container: {task['payload']['container_name']}")
            print(f"   - Command: {task['payload']['command']}")
    
    # Key features summary
    print_section("6. Key Features Demonstrated")
    print("""
   ✓ Time Window Control (03:00-08:00)
   ✓ Video Downloads (YouTube, X/Twitter, etc.)
   ✓ Telegram Video Downloads (with Telethon)
   ✓ Library Installation (Shell commands)
   ✓ Docker Integration (Container execution)
   ✓ Task Persistence (JSON storage)
   ✓ Resumable Downloads (Chunk-based window checking)
   ✓ Multiple Task Types
   ✓ Status Tracking
    """)
    
    # Next steps
    print_section("7. Next Steps")
    print("""
   To start processing these tasks:
   
   1. Ensure the current time is within 03:00-08:00
   2. Run the download manager:
      
      python3 download_manager.py
      
      Or using the CLI:
      
      python3 cli.py run
      
      Or if installed via pip:
      
      nightshift run
   
   3. The manager will:
      - Check the time window every minute
      - Process pending tasks when within window
      - Pause tasks when outside window
      - Save progress continuously
      - Resume tasks on next time window
    """)
    
    print_section("Demo Complete")
    print(f"\n   Tasks saved in: demo_tasks.json")
    print(f"   To clean up: rm demo_tasks.json\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
