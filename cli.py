#!/usr/bin/env python3
"""
CLI interface for NightShift-lDownloader
"""

import argparse
import sys
from download_manager import DownloadManager, TaskType


def main():
    parser = argparse.ArgumentParser(
        description='NightShift-lDownloader - Time-window based download manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a video download task
  %(prog)s add-video "https://www.youtube.com/watch?v=example"
  
  # Add a Telegram video download task
  %(prog)s add-telegram "https://t.me/channel/123"
  
  # Add a library installation task
  %(prog)s add-install "pip install torch"
  
  # Add a Docker library installation task
  %(prog)s add-docker my_container "pip install torch"
  
  # Start the download manager
  %(prog)s run
  
  # List all tasks
  %(prog)s list
        """
    )
    
    parser.add_argument(
        '--tasks-file',
        default='tasks.json',
        help='Path to tasks JSON file (default: tasks.json)'
    )
    
    parser.add_argument(
        '--download-dir',
        default='downloads',
        help='Download directory (default: downloads)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add video download command
    add_video_parser = subparsers.add_parser('add-video', help='Add a video download task')
    add_video_parser.add_argument('url', help='Video URL (YouTube, X/Twitter, etc.)')
    add_video_parser.add_argument('--cookie-file', help='Path to cookie file for authentication')
    
    # Add Telegram download command
    add_telegram_parser = subparsers.add_parser('add-telegram', help='Add a Telegram video download task')
    add_telegram_parser.add_argument('url', help='Telegram message URL')
    add_telegram_parser.add_argument('--api-id', help='Telegram API ID')
    add_telegram_parser.add_argument('--api-hash', help='Telegram API hash')
    add_telegram_parser.add_argument('--phone', help='Phone number')
    
    # Add library install command
    add_install_parser = subparsers.add_parser('add-install', help='Add a library installation task')
    add_install_parser.add_argument('command', help='Shell command to execute')
    
    # Add Docker install command
    add_docker_parser = subparsers.add_parser('add-docker', help='Add a Docker library installation task')
    add_docker_parser.add_argument('container', help='Docker container name')
    add_docker_parser.add_argument('command', help='Command to execute in container')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Start the download manager')
    run_parser.add_argument(
        '--check-interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    
    # List command
    subparsers.add_parser('list', help='List all tasks')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize manager
    manager = DownloadManager(
        tasks_file=args.tasks_file,
        download_dir=args.download_dir
    )
    
    # Execute command
    if args.command == 'add-video':
        payload = {'url': args.url}
        if args.cookie_file:
            payload['cookie_file'] = args.cookie_file
        task_id = manager.add_task(TaskType.VIDEO_DOWNLOAD.value, payload)
        print(f"✓ Added video download task: {task_id}")
        print(f"  URL: {args.url}")
        
    elif args.command == 'add-telegram':
        payload = {'url': args.url}
        if args.api_id:
            payload['api_id'] = args.api_id
        if args.api_hash:
            payload['api_hash'] = args.api_hash
        if args.phone:
            payload['phone'] = args.phone
        task_id = manager.add_task(TaskType.TELEGRAM_VIDEO.value, payload)
        print(f"✓ Added Telegram video download task: {task_id}")
        print(f"  URL: {args.url}")
        
    elif args.command == 'add-install':
        payload = {'command': args.command}
        task_id = manager.add_task(TaskType.LIBRARY_INSTALL.value, payload)
        print(f"✓ Added library installation task: {task_id}")
        print(f"  Command: {args.command}")
        
    elif args.command == 'add-docker':
        payload = {
            'container_name': args.container,
            'command': args.command
        }
        task_id = manager.add_task(TaskType.LIBRARY_INSTALL.value, payload)
        print(f"✓ Added Docker library installation task: {task_id}")
        print(f"  Container: {args.container}")
        print(f"  Command: {args.command}")
        
    elif args.command == 'run':
        print("Starting NightShift-lDownloader...")
        print(f"Time window: 03:00 - 08:00")
        print(f"Check interval: {args.check_interval} seconds")
        print(f"Tasks file: {args.tasks_file}")
        print(f"Download directory: {args.download_dir}")
        print("\nPress Ctrl+C to stop\n")
        try:
            manager.run(check_interval=args.check_interval)
        except KeyboardInterrupt:
            print("\n\nStopping download manager...")
            manager.stop()
            
    elif args.command == 'list':
        if not manager.tasks:
            print("No tasks found.")
            return 0
        
        print(f"Total tasks: {len(manager.tasks)}\n")
        
        status_counts = {}
        for task in manager.tasks:
            status = task['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("Status summary:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
        
        print("\nTask details:")
        for i, task in enumerate(manager.tasks, 1):
            print(f"\n{i}. Task ID: {task['id']}")
            print(f"   Type: {task['type']}")
            print(f"   Status: {task['status']}")
            print(f"   Created: {task['created_at']}")
            
            if task['type'] == TaskType.VIDEO_DOWNLOAD.value:
                print(f"   URL: {task['payload'].get('url', 'N/A')}")
            elif task['type'] == TaskType.TELEGRAM_VIDEO.value:
                print(f"   URL: {task['payload'].get('url', 'N/A')}")
            elif task['type'] == TaskType.LIBRARY_INSTALL.value:
                if 'container_name' in task['payload']:
                    print(f"   Container: {task['payload']['container_name']}")
                print(f"   Command: {task['payload'].get('command', 'N/A')}")
            
            if task.get('progress'):
                print(f"   Progress: {task['progress']}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
