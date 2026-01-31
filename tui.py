#!/usr/bin/env python3
"""
Terminal User Interface (TUI) for NightShift-lDownloader
Provides an interactive menu-based interface for managing download tasks
"""

import os
import sys
from datetime import datetime
from download_manager import DownloadManager, TaskType, TaskStatus


class SimpleTUI:
    """Simple text-based menu interface that works in any terminal"""
    
    def __init__(self, tasks_file="tasks.json", download_dir="downloads"):
        self.manager = DownloadManager(tasks_file=tasks_file, download_dir=download_dir)
        self.running = True
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Print the application header"""
        print("=" * 70)
        print("  NightShift-lDownloader - Task Management Interface")
        print("=" * 70)
        print()
    
    def print_tasks(self):
        """Display all tasks in a formatted table"""
        if not self.manager.tasks:
            print("📭 No tasks found.")
            print()
            return
        
        print(f"Total tasks: {len(self.manager.tasks)}")
        print()
        
        # Group by status
        status_groups = {}
        for task in self.manager.tasks:
            status = task['status']
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(task)
        
        # Print status summary
        print("Status Summary:")
        status_icons = {
            'pending': '⏳',
            'in_progress': '▶️',
            'completed': '✅',
            'failed': '❌',
            'paused': '⏸️'
        }
        for status, count in sorted([(s, len(tasks)) for s, tasks in status_groups.items()]):
            icon = status_icons.get(status, '•')
            print(f"  {icon} {status}: {count}")
        print()
        
        # Print detailed task list
        print("-" * 70)
        for i, task in enumerate(self.manager.tasks, 1):
            status_icon = status_icons.get(task['status'], '•')
            print(f"{i}. [{status_icon}] {task['id']}")
            print(f"   Type: {task['type']}")
            print(f"   Status: {task['status']}")
            
            if task['type'] == TaskType.VIDEO_DOWNLOAD.value:
                url = task['payload'].get('url', 'N/A')
                # Truncate long URLs
                if len(url) > 60:
                    url = url[:57] + "..."
                print(f"   URL: {url}")
            elif task['type'] == TaskType.TELEGRAM_VIDEO.value:
                url = task['payload'].get('url', 'N/A')
                if len(url) > 60:
                    url = url[:57] + "..."
                print(f"   URL: {url}")
            elif task['type'] == TaskType.LIBRARY_INSTALL.value:
                if 'container_name' in task['payload']:
                    print(f"   Container: {task['payload']['container_name']}")
                print(f"   Command: {task['payload'].get('command', 'N/A')}")
            
            if task.get('progress'):
                progress = task['progress']
                if 'percent' in progress:
                    print(f"   Progress: {progress['percent']:.1f}%")
                elif 'downloaded' in progress and 'total' in progress:
                    downloaded = progress['downloaded']
                    total = progress['total']
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"   Progress: {pct:.1f}% ({downloaded}/{total} bytes)")
            
            print(f"   Created: {task['created_at']}")
            print()
        print("-" * 70)
    
    def print_menu(self):
        """Print the main menu"""
        print("\nMain Menu:")
        print("  1. View all tasks")
        print("  2. Add a new task")
        print("  3. Delete a task")
        print("  4. View task details")
        print("  5. Check time window status")
        print("  6. Start download manager")
        print("  0. Exit")
        print()
    
    def get_input(self, prompt):
        """Get user input with a prompt"""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return None
    
    def view_tasks(self):
        """View all tasks"""
        self.clear_screen()
        self.print_header()
        print("📋 Task List")
        print()
        self.print_tasks()
        self.get_input("\nPress Enter to continue...")
    
    def add_task_menu(self):
        """Interactive menu for adding a new task"""
        self.clear_screen()
        self.print_header()
        print("➕ Add New Task")
        print()
        print("Task Types:")
        print("  1. Video Download (YouTube, X/Twitter, etc.)")
        print("  2. Telegram Video Download")
        print("  3. Library Installation (Shell command)")
        print("  4. Library Installation (Docker)")
        print("  0. Cancel")
        print()
        
        choice = self.get_input("Select task type: ")
        
        if choice == '1':
            self._add_video_task()
        elif choice == '2':
            self._add_telegram_task()
        elif choice == '3':
            self._add_shell_task()
        elif choice == '4':
            self._add_docker_task()
    
    def _add_video_task(self):
        """Add a video download task"""
        print("\n📹 Add Video Download Task")
        print()
        url = self.get_input("Enter video URL: ")
        if not url:
            print("❌ URL is required")
            self.get_input("\nPress Enter to continue...")
            return
        
        cookie_file = self.get_input("Enter cookie file path (optional, press Enter to skip): ")
        
        payload = {'url': url}
        if cookie_file:
            payload['cookie_file'] = cookie_file
        
        task_id = self.manager.add_task(TaskType.VIDEO_DOWNLOAD.value, payload)
        print(f"\n✅ Task added successfully: {task_id}")
        self.get_input("\nPress Enter to continue...")
    
    def _add_telegram_task(self):
        """Add a Telegram video download task"""
        print("\n📱 Add Telegram Video Download Task")
        print()
        url = self.get_input("Enter Telegram message URL: ")
        if not url:
            print("❌ URL is required")
            self.get_input("\nPress Enter to continue...")
            return
        
        payload = {'url': url}
        
        # Check if credentials should be provided
        provide_creds = self.get_input("Provide API credentials now? (y/n, default: n): ").lower()
        if provide_creds == 'y':
            api_id = self.get_input("Telegram API ID: ")
            api_hash = self.get_input("Telegram API Hash: ")
            phone = self.get_input("Phone number: ")
            
            if api_id:
                payload['api_id'] = api_id
            if api_hash:
                payload['api_hash'] = api_hash
            if phone:
                payload['phone'] = phone
        
        task_id = self.manager.add_task(TaskType.TELEGRAM_VIDEO.value, payload)
        print(f"\n✅ Task added successfully: {task_id}")
        self.get_input("\nPress Enter to continue...")
    
    def _add_shell_task(self):
        """Add a shell command task"""
        print("\n💻 Add Library Installation Task (Shell)")
        print()
        command = self.get_input("Enter shell command: ")
        if not command:
            print("❌ Command is required")
            self.get_input("\nPress Enter to continue...")
            return
        
        payload = {'command': command}
        task_id = self.manager.add_task(TaskType.LIBRARY_INSTALL.value, payload)
        print(f"\n✅ Task added successfully: {task_id}")
        print("⚠️  Note: Shell commands will be executed with shell=True. Ensure the command is from a trusted source.")
        self.get_input("\nPress Enter to continue...")
    
    def _add_docker_task(self):
        """Add a Docker command task"""
        print("\n🐳 Add Library Installation Task (Docker)")
        print()
        container = self.get_input("Enter Docker container name: ")
        if not container:
            print("❌ Container name is required")
            self.get_input("\nPress Enter to continue...")
            return
        
        command = self.get_input("Enter command to execute in container: ")
        if not command:
            print("❌ Command is required")
            self.get_input("\nPress Enter to continue...")
            return
        
        payload = {
            'container_name': container,
            'command': command
        }
        task_id = self.manager.add_task(TaskType.LIBRARY_INSTALL.value, payload)
        print(f"\n✅ Task added successfully: {task_id}")
        self.get_input("\nPress Enter to continue...")
    
    def delete_task_menu(self):
        """Interactive menu for deleting a task"""
        self.clear_screen()
        self.print_header()
        print("🗑️  Delete Task")
        print()
        
        if not self.manager.tasks:
            print("📭 No tasks to delete.")
            self.get_input("\nPress Enter to continue...")
            return
        
        # Show tasks with numbers
        for i, task in enumerate(self.manager.tasks, 1):
            print(f"{i}. {task['id']} - {task['type']} ({task['status']})")
        
        print()
        task_num = self.get_input("Enter task number to delete (0 to cancel): ")
        
        try:
            task_num = int(task_num)
            if task_num == 0:
                return
            if 1 <= task_num <= len(self.manager.tasks):
                task = self.manager.tasks[task_num - 1]
                confirm = self.get_input(f"Are you sure you want to delete task '{task['id']}'? (y/n): ")
                if confirm.lower() == 'y':
                    self.manager.tasks.pop(task_num - 1)
                    self.manager.save_tasks()
                    print("\n✅ Task deleted successfully")
                else:
                    print("\n❌ Deletion cancelled")
            else:
                print("\n❌ Invalid task number")
        except ValueError:
            print("\n❌ Invalid input")
        
        self.get_input("\nPress Enter to continue...")
    
    def view_task_details(self):
        """View detailed information about a specific task"""
        self.clear_screen()
        self.print_header()
        print("🔍 View Task Details")
        print()
        
        if not self.manager.tasks:
            print("📭 No tasks available.")
            self.get_input("\nPress Enter to continue...")
            return
        
        # Show tasks with numbers
        for i, task in enumerate(self.manager.tasks, 1):
            print(f"{i}. {task['id']} - {task['type']} ({task['status']})")
        
        print()
        task_num = self.get_input("Enter task number to view (0 to cancel): ")
        
        try:
            task_num = int(task_num)
            if task_num == 0:
                return
            if 1 <= task_num <= len(self.manager.tasks):
                task = self.manager.tasks[task_num - 1]
                
                print("\n" + "=" * 70)
                print(f"Task: {task['id']}")
                print("=" * 70)
                print(f"Type: {task['type']}")
                print(f"Status: {task['status']}")
                print(f"Created: {task['created_at']}")
                print(f"Updated: {task['updated_at']}")
                print()
                print("Payload:")
                for key, value in task['payload'].items():
                    print(f"  {key}: {value}")
                
                if task.get('progress'):
                    print()
                    print("Progress:")
                    for key, value in task['progress'].items():
                        print(f"  {key}: {value}")
                
                print("=" * 70)
            else:
                print("\n❌ Invalid task number")
        except ValueError:
            print("\n❌ Invalid input")
        
        self.get_input("\nPress Enter to continue...")
    
    def check_time_window(self):
        """Check and display the current time window status"""
        self.clear_screen()
        self.print_header()
        print("⏰ Time Window Status")
        print()
        
        current_time = datetime.now().strftime("%H:%M:%S")
        is_within = self.manager.is_within_window()
        
        print(f"Current time: {current_time}")
        print(f"Time window: 03:00:00 - 08:00:00")
        print()
        
        if is_within:
            print("✅ STATUS: WITHIN WINDOW")
            print("   Tasks will be processed.")
        else:
            print("⏸️  STATUS: OUTSIDE WINDOW")
            print("   Tasks are suspended until the next time window.")
        
        print()
        self.get_input("Press Enter to continue...")
    
    def start_manager(self):
        """Start the download manager"""
        self.clear_screen()
        self.print_header()
        print("▶️  Start Download Manager")
        print()
        print("This will start the download manager in the background.")
        print("Tasks will be processed during the time window (03:00-08:00).")
        print()
        print("Note: This TUI does not support running the manager interactively.")
        print("Please use 'nightshift run' in a separate terminal to start the manager.")
        print()
        self.get_input("Press Enter to continue...")
    
    def run(self):
        """Main TUI loop"""
        while self.running:
            self.clear_screen()
            self.print_header()
            
            # Show current status
            current_time = datetime.now().strftime("%H:%M:%S")
            is_within = self.manager.is_within_window()
            status = "✅ ACTIVE" if is_within else "⏸️  SUSPENDED"
            
            print(f"Time: {current_time} | Window: 03:00-08:00 | Status: {status}")
            print(f"Tasks: {len(self.manager.tasks)}")
            print()
            
            self.print_menu()
            
            choice = self.get_input("Enter your choice: ")
            
            if choice == '1':
                self.view_tasks()
            elif choice == '2':
                self.add_task_menu()
            elif choice == '3':
                self.delete_task_menu()
            elif choice == '4':
                self.view_task_details()
            elif choice == '5':
                self.check_time_window()
            elif choice == '6':
                self.start_manager()
            elif choice == '0':
                print("\n👋 Goodbye!")
                self.running = False
            else:
                print("\n❌ Invalid choice. Please try again.")
                self.get_input("\nPress Enter to continue...")


def main():
    """Entry point for the TUI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='NightShift-lDownloader - Interactive Task Management Interface'
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
    
    args = parser.parse_args()
    
    try:
        tui = SimpleTUI(tasks_file=args.tasks_file, download_dir=args.download_dir)
        tui.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
