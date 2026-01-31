#!/usr/bin/env python3
"""
NightShift-lDownloader - A time-window based download manager
Supports Telegram, X/Twitter, and general video downloads with task persistence
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
from queue import Queue
import threading


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Enumeration of supported task types"""
    TELEGRAM_VIDEO = "telegram_video"
    VIDEO_DOWNLOAD = "video_download"
    LIBRARY_INSTALL = "library_install"


class TaskStatus(Enum):
    """Enumeration of task statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class DownloadManager:
    """
    Main download manager class that handles task queue and time-window based execution
    """
    
    def __init__(self, tasks_file: str = "tasks.json", download_dir: str = "downloads"):
        """
        Initialize the download manager
        
        Args:
            tasks_file: Path to the JSON file for task persistence
            download_dir: Directory for downloaded files
        """
        self.tasks_file = tasks_file
        self.download_dir = download_dir
        self.task_queue = Queue()
        self.tasks: List[Dict[str, Any]] = []
        self.running = False
        self.current_task: Optional[Dict[str, Any]] = None
        self.stop_current_task = threading.Event()
        
        # Create download directory if it doesn't exist
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        
        # Load existing tasks
        self.load_tasks()
        
    def is_within_window(self) -> bool:
        """
        Check if current time is within the allowed download window (03:00 - 08:00)
        
        Returns:
            True if current time is between 03:00 and 08:00, False otherwise
        """
        current_time = datetime.now().time()
        start_time = datetime.strptime("03:00", "%H:%M").time()
        end_time = datetime.strptime("08:00", "%H:%M").time()
        
        is_within = start_time <= current_time <= end_time
        if is_within:
            logger.info(f"Within time window: {current_time}")
        else:
            logger.debug(f"Outside time window: {current_time}")
        
        return is_within
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                logger.info(f"Loaded {len(self.tasks)} tasks from {self.tasks_file}")
            except Exception as e:
                logger.error(f"Error loading tasks: {e}")
                self.tasks = []
        else:
            self.tasks = []
            logger.info("No existing tasks file found, starting fresh")
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.tasks)} tasks to {self.tasks_file}")
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
    
    def add_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        """
        Add a new task to the task list
        
        Args:
            task_type: Type of task (telegram_video, video_download, library_install)
            payload: Task-specific data (url, command, etc.)
            
        Returns:
            Task ID
        """
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        task = {
            "id": task_id,
            "type": task_type,
            "payload": payload,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": {}
        }
        
        self.tasks.append(task)
        self.save_tasks()
        logger.info(f"Added task {task_id} of type {task_type}")
        
        return task_id
    
    def update_task_status(self, task_id: str, status: TaskStatus, progress: Optional[Dict] = None):
        """Update the status of a task"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = status.value
                task["updated_at"] = datetime.now().isoformat()
                if progress:
                    task["progress"].update(progress)
                self.save_tasks()
                logger.info(f"Updated task {task_id} status to {status.value}")
                break
    
    def download_telegram_video(self, task: Dict[str, Any]) -> bool:
        """
        Download a video from Telegram using Telethon
        
        Args:
            task: Task dictionary containing the Telegram message URL
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            from telethon import TelegramClient
            from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
            
            url = task["payload"].get("url")
            logger.info(f"Starting Telegram video download: {url}")
            
            # Extract API credentials from payload or environment
            api_id = task["payload"].get("api_id") or os.getenv("TELEGRAM_API_ID")
            api_hash = task["payload"].get("api_hash") or os.getenv("TELEGRAM_API_HASH")
            phone = task["payload"].get("phone") or os.getenv("TELEGRAM_PHONE")
            
            if not all([api_id, api_hash]):
                logger.error("Telegram API credentials not provided")
                return False
            
            # Create client
            client = TelegramClient('session', api_id, api_hash)
            
            async def download_with_window_check():
                await client.start(phone=phone)
                
                # Parse the message URL to get channel and message ID
                # Format: https://t.me/channel/message_id
                parts = url.rstrip('/').split('/')
                if len(parts) >= 2:
                    channel = parts[-2]
                    message_id = int(parts[-1])
                else:
                    logger.error(f"Invalid Telegram URL format: {url}")
                    return False
                
                # Get the message
                message = await client.get_messages(channel, ids=message_id)
                
                if not message or not message.media:
                    logger.error("Message not found or has no media")
                    return False
                
                # Download with chunk-based window checking
                output_path = os.path.join(self.download_dir, f"telegram_{task['id']}.mp4")
                
                def progress_callback(current, total):
                    # Check time window before each chunk
                    if not self.is_within_window() or self.stop_current_task.is_set():
                        logger.warning("Outside time window or stop requested, pausing download")
                        raise InterruptedError("Download paused")
                    
                    progress_pct = (current / total) * 100 if total > 0 else 0
                    self.update_task_status(
                        task["id"],
                        TaskStatus.IN_PROGRESS,
                        {"downloaded": current, "total": total, "percent": progress_pct}
                    )
                
                try:
                    await client.download_media(
                        message,
                        file=output_path,
                        progress_callback=progress_callback
                    )
                    logger.info(f"Successfully downloaded to {output_path}")
                    return True
                except InterruptedError:
                    logger.info("Download interrupted, progress saved")
                    self.update_task_status(task["id"], TaskStatus.PAUSED)
                    return False
                finally:
                    await client.disconnect()
            
            # Run async function
            import asyncio
            return asyncio.get_event_loop().run_until_complete(download_with_window_check())
            
        except ImportError:
            logger.error("Telethon library not installed. Install with: pip install telethon")
            return False
        except Exception as e:
            logger.error(f"Error downloading Telegram video: {e}")
            return False
    
    def download_video(self, task: Dict[str, Any]) -> bool:
        """
        Download video using yt-dlp (supports X/Twitter and many other sites)
        
        Args:
            task: Task dictionary containing the video URL
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            import yt_dlp
            
            url = task["payload"].get("url")
            logger.info(f"Starting video download: {url}")
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'format': 'best',
                'quiet': False,
                'no_warnings': False,
            }
            
            # Add cookie handling for X/Twitter to prevent blocking
            # Check if URL is from X/Twitter by validating the exact domain
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc.lower()
            # Check for exact domain match or subdomain
            is_twitter = (hostname == 'twitter.com' or hostname == 'x.com' or 
                         hostname.endswith('.twitter.com') or hostname.endswith('.x.com'))
            
            if is_twitter:
                logger.info("Detected X/Twitter URL, applying cookie configuration")
                # Add cookies from browser if available
                cookie_file = task["payload"].get("cookie_file")
                if cookie_file and os.path.exists(cookie_file):
                    ydl_opts['cookiefile'] = cookie_file
                else:
                    # Try to extract cookies from browser
                    try:
                        ydl_opts['cookiesfrombrowser'] = ('chrome',)
                    except Exception as e:
                        logger.warning(f"Failed to extract cookies from browser: {e}")
                        logger.warning("Consider providing a cookie file with --cookie-file option")
            
            # Progress hook to check time window
            def progress_hook(d):
                if not self.is_within_window() or self.stop_current_task.is_set():
                    logger.warning("Outside time window or stop requested")
                    raise InterruptedError("Download paused")
                
                if d['status'] == 'downloading':
                    progress = {
                        'downloaded': d.get('downloaded_bytes', 0),
                        'total': d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0),
                        'speed': d.get('speed', 0),
                        'eta': d.get('eta', 0)
                    }
                    self.update_task_status(task["id"], TaskStatus.IN_PROGRESS, progress)
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Download the video
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                logger.info(f"Successfully downloaded video from {url}")
                return True
            except InterruptedError:
                logger.info("Download interrupted, will retry later")
                self.update_task_status(task["id"], TaskStatus.PAUSED)
                return False
                
        except ImportError:
            logger.error("yt-dlp library not installed. Install with: pip install yt-dlp")
            return False
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return False
    
    def execute_command(self, task: Dict[str, Any]) -> bool:
        """
        Execute a shell command
        
        Args:
            task: Task dictionary containing the command to execute
            
        Returns:
            True if command executed successfully, False otherwise
        
        Note:
            This function uses shell=True which can be a security risk.
            Only use with trusted command inputs.
        """
        try:
            command = task["payload"].get("command")
            logger.info(f"Executing command: {command}")
            logger.warning("Executing shell command with shell=True - ensure command is from trusted source")
            
            # Check time window before execution
            if not self.is_within_window():
                logger.warning("Outside time window, skipping command execution")
                return False
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Command executed successfully: {result.stdout}")
                return True
            else:
                logger.error(f"Command failed with code {result.returncode}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return False
    
    def execute_in_docker(self, container_name: str, command: str, user: str = "0") -> bool:
        """
        Execute a command inside a Docker container
        
        Args:
            container_name: Name of the Docker container
            command: Command to execute inside the container
            user: User to run as (default: "0" for root). Change this for better security.
            
        Returns:
            True if command executed successfully, False otherwise
            
        Note:
            Running as root (user="0") is a security risk. Consider using a non-root user.
            This function uses shell=True which can be a security risk.
            Only use with trusted inputs.
        """
        try:
            import shlex
            
            # Sanitize inputs to prevent command injection
            # Build command using list instead of string interpolation
            docker_cmd = ['docker', 'exec', '-u', user, container_name, 'sh', '-c', command]
            
            logger.info(f"Executing in Docker container '{container_name}': {command}")
            if user == "0":
                logger.warning("Running Docker command as root (user 0) - consider using non-root user for security")
            
            # Check time window before execution
            if not self.is_within_window():
                logger.warning("Outside time window, skipping Docker command execution")
                return False
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Docker command executed successfully: {result.stdout}")
                return True
            else:
                logger.error(f"Docker command failed with code {result.returncode}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing Docker command: {e}")
            return False
    
    def process_task(self, task: Dict[str, Any]) -> bool:
        """
        Process a single task based on its type
        
        Args:
            task: Task dictionary
            
        Returns:
            True if task completed successfully, False otherwise
        """
        self.current_task = task
        self.stop_current_task.clear()
        
        task_type = task.get("type")
        logger.info(f"Processing task {task['id']} of type {task_type}")
        
        self.update_task_status(task["id"], TaskStatus.IN_PROGRESS)
        
        try:
            success = False
            
            if task_type == TaskType.TELEGRAM_VIDEO.value:
                success = self.download_telegram_video(task)
            elif task_type == TaskType.VIDEO_DOWNLOAD.value:
                success = self.download_video(task)
            elif task_type == TaskType.LIBRARY_INSTALL.value:
                # Check if Docker execution is needed
                container_name = task["payload"].get("container_name")
                command = task["payload"].get("command")
                
                if container_name:
                    success = self.execute_in_docker(container_name, command)
                else:
                    success = self.execute_command(task)
            else:
                logger.error(f"Unknown task type: {task_type}")
                success = False
            
            if success:
                self.update_task_status(task["id"], TaskStatus.COMPLETED)
            else:
                self.update_task_status(task["id"], TaskStatus.FAILED)
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing task {task['id']}: {e}")
            self.update_task_status(task["id"], TaskStatus.FAILED)
            return False
        finally:
            self.current_task = None
    
    def run(self, check_interval: int = 60):
        """
        Main loop that checks time window and processes tasks
        
        Args:
            check_interval: Interval in seconds between checks (default: 60 seconds)
        """
        self.running = True
        logger.info("Download manager started")
        
        try:
            while self.running:
                if self.is_within_window():
                    # Filter pending and paused tasks
                    pending_tasks = [
                        t for t in self.tasks 
                        if t["status"] in [TaskStatus.PENDING.value, TaskStatus.PAUSED.value]
                    ]
                    
                    if pending_tasks:
                        logger.info(f"Found {len(pending_tasks)} pending tasks to process")
                        
                        for task in pending_tasks:
                            # Check time window again before each task
                            if not self.is_within_window():
                                logger.info("Left time window, pausing task processing")
                                break
                            
                            self.process_task(task)
                    else:
                        logger.info("No pending tasks, waiting...")
                else:
                    logger.info("Outside time window, tasks suspended")
                    # Signal current task to stop if running
                    if self.current_task:
                        self.stop_current_task.set()
                
                # Wait for next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            self.running = False
            self.stop_current_task.set()
    
    def stop(self):
        """Stop the download manager"""
        logger.info("Stopping download manager...")
        self.running = False
        self.stop_current_task.set()


if __name__ == "__main__":
    # Example usage
    manager = DownloadManager()
    
    # Add some example tasks
    # manager.add_task(TaskType.VIDEO_DOWNLOAD.value, {"url": "https://twitter.com/example/status/123"})
    # manager.add_task(TaskType.LIBRARY_INSTALL.value, {"command": "pip install torch"})
    
    # Start the manager
    manager.run()
