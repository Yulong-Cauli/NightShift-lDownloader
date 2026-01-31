#!/usr/bin/env python3
"""
Test script for NightShift-lDownloader
Tests basic functionality without requiring actual downloads
"""

import sys
import os
from datetime import datetime, time
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_manager import DownloadManager, TaskType, TaskStatus


def test_time_window():
    """Test the time window function"""
    print("Testing time window function...")
    
    manager = DownloadManager(tasks_file="/tmp/test_tasks.json", download_dir="/tmp/test_downloads")
    
    # Test with mocked datetime
    with patch('download_manager.datetime') as mock_datetime:
        # Test time inside window (05:00)
        mock_now = MagicMock()
        mock_now.time.return_value = time(5, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime = datetime.strptime  # Keep real strptime
        assert manager.is_within_window() == True, "05:00 should be within window"
        print("  ✓ 05:00 correctly identified as within window")
        
        # Test time outside window (10:00)
        mock_now.time.return_value = time(10, 0)
        assert manager.is_within_window() == False, "10:00 should be outside window"
        print("  ✓ 10:00 correctly identified as outside window")
        
        # Test edge cases
        mock_now.time.return_value = time(3, 0)
        assert manager.is_within_window() == True, "03:00 should be within window"
        print("  ✓ 03:00 (start) correctly identified as within window")
        
        mock_now.time.return_value = time(8, 0)
        assert manager.is_within_window() == True, "08:00 should be within window"
        print("  ✓ 08:00 (end) correctly identified as within window")
        
        mock_now.time.return_value = time(2, 59)
        assert manager.is_within_window() == False, "02:59 should be outside window"
        print("  ✓ 02:59 correctly identified as outside window")
        
        mock_now.time.return_value = time(8, 1)
        assert manager.is_within_window() == False, "08:01 should be outside window"
        print("  ✓ 08:01 correctly identified as outside window")
    
    print("✅ Time window function tests passed!\n")


def test_task_management():
    """Test task addition and persistence"""
    print("Testing task management...")
    
    # Clean up any existing test files
    test_file = "/tmp/test_tasks.json"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    manager = DownloadManager(tasks_file=test_file, download_dir="/tmp/test_downloads")
    
    # Test adding tasks
    task_id_1 = manager.add_task(
        TaskType.VIDEO_DOWNLOAD.value,
        {"url": "https://example.com/video"}
    )
    assert task_id_1 is not None, "Task ID should not be None"
    print(f"  ✓ Added video download task: {task_id_1}")
    
    task_id_2 = manager.add_task(
        TaskType.LIBRARY_INSTALL.value,
        {"command": "echo 'test'"}
    )
    assert task_id_2 is not None, "Task ID should not be None"
    print(f"  ✓ Added library install task: {task_id_2}")
    
    # Verify tasks were saved
    assert len(manager.tasks) == 2, "Should have 2 tasks"
    print(f"  ✓ Task count correct: {len(manager.tasks)}")
    
    # Verify persistence
    manager2 = DownloadManager(tasks_file=test_file, download_dir="/tmp/test_downloads")
    assert len(manager2.tasks) == 2, "Tasks should persist across instances"
    print(f"  ✓ Tasks persisted correctly")
    
    # Test task status update
    manager.update_task_status(task_id_1, TaskStatus.COMPLETED)
    task = next(t for t in manager.tasks if t['id'] == task_id_1)
    assert task["status"] == TaskStatus.COMPLETED.value
    print(f"  ✓ Task status updated correctly")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("✅ Task management tests passed!\n")


def test_task_types():
    """Test that all task types are properly defined"""
    print("Testing task types...")
    
    assert TaskType.TELEGRAM_VIDEO.value == "telegram_video"
    print("  ✓ TELEGRAM_VIDEO type defined")
    
    assert TaskType.VIDEO_DOWNLOAD.value == "video_download"
    print("  ✓ VIDEO_DOWNLOAD type defined")
    
    assert TaskType.LIBRARY_INSTALL.value == "library_install"
    print("  ✓ LIBRARY_INSTALL type defined")
    
    print("✅ Task type tests passed!\n")


def test_task_statuses():
    """Test that all task statuses are properly defined"""
    print("Testing task statuses...")
    
    assert TaskStatus.PENDING.value == "pending"
    print("  ✓ PENDING status defined")
    
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    print("  ✓ IN_PROGRESS status defined")
    
    assert TaskStatus.COMPLETED.value == "completed"
    print("  ✓ COMPLETED status defined")
    
    assert TaskStatus.FAILED.value == "failed"
    print("  ✓ FAILED status defined")
    
    assert TaskStatus.PAUSED.value == "paused"
    print("  ✓ PAUSED status defined")
    
    print("✅ Task status tests passed!\n")


def test_downloads_directory():
    """Test that downloads directory is created"""
    print("Testing downloads directory creation...")
    
    test_dir = "/tmp/test_dl_dir"
    if os.path.exists(test_dir):
        os.rmdir(test_dir)
    
    manager = DownloadManager(tasks_file="/tmp/test_tasks.json", download_dir=test_dir)
    
    assert os.path.exists(test_dir), "Downloads directory should be created"
    print(f"  ✓ Downloads directory created: {test_dir}")
    
    # Clean up
    if os.path.exists(test_dir):
        os.rmdir(test_dir)
    
    print("✅ Downloads directory tests passed!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("NightShift-lDownloader - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_time_window()
        test_task_management()
        test_task_types()
        test_task_statuses()
        test_downloads_directory()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
