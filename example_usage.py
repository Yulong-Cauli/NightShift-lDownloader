#!/usr/bin/env python3
"""
Example usage of NightShift-lDownloader
"""

from download_manager import DownloadManager, TaskType
import os


def main():
    """Demonstrate the download manager usage"""
    
    # Initialize the download manager
    manager = DownloadManager(
        tasks_file="tasks.json",
        download_dir="downloads"
    )
    
    print("=" * 60)
    print("NightShift-lDownloader - Example Usage")
    print("=" * 60)
    print()
    
    # Example 1: Add a video download task (works with YouTube, X/Twitter, etc.)
    print("1. Adding a video download task...")
    task_id_1 = manager.add_task(
        TaskType.VIDEO_DOWNLOAD.value,
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            # For X/Twitter videos, you can optionally provide a cookie file
            # "cookie_file": "/path/to/cookies.txt"
        }
    )
    print(f"   Added task: {task_id_1}")
    print()
    
    # Example 2: Add a Telegram video download task
    print("2. Adding a Telegram video download task...")
    # Note: You need to set up Telegram API credentials
    # Either through environment variables or in the payload
    task_id_2 = manager.add_task(
        TaskType.TELEGRAM_VIDEO.value,
        {
            "url": "https://t.me/channel_name/123",
            # Optional: provide credentials here if not in environment
            # "api_id": "YOUR_API_ID",
            # "api_hash": "YOUR_API_HASH",
            # "phone": "+1234567890"
        }
    )
    print(f"   Added task: {task_id_2}")
    print()
    
    # Example 3: Add a library installation task (regular shell command)
    print("3. Adding a library installation task...")
    task_id_3 = manager.add_task(
        TaskType.LIBRARY_INSTALL.value,
        {
            "command": "pip install requests"
        }
    )
    print(f"   Added task: {task_id_3}")
    print()
    
    # Example 4: Add a library installation task in Docker
    print("4. Adding a Docker library installation task...")
    task_id_4 = manager.add_task(
        TaskType.LIBRARY_INSTALL.value,
        {
            "container_name": "my_container",
            "command": "pip install torch"
        }
    )
    print(f"   Added task: {task_id_4}")
    print()
    
    # Example 5: Add multiple X/Twitter video downloads
    print("5. Adding X/Twitter video download tasks...")
    twitter_urls = [
        "https://x.com/user/status/123456789",
        "https://twitter.com/user/status/987654321"
    ]
    for url in twitter_urls:
        task_id = manager.add_task(
            TaskType.VIDEO_DOWNLOAD.value,
            {"url": url}
        )
        print(f"   Added task: {task_id} for {url}")
    print()
    
    print("=" * 60)
    print("All tasks added successfully!")
    print("=" * 60)
    print()
    print("To start the download manager, run:")
    print("  python3 download_manager.py")
    print()
    print("Tasks will only be processed during the time window:")
    print("  03:00 - 08:00")
    print()
    print("Tasks are saved in: tasks.json")
    print("Downloads are saved in: downloads/")
    print()
    
    # Don't start the manager in example mode, just add tasks
    # To actually run the manager, uncomment the line below:
    # manager.run()


if __name__ == "__main__":
    main()
