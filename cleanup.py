#!/usr/bin/env python3
"""
Cleanup Script for PDF Editor Web App
Removes session folders older than 2 hours to prevent storage bloat

This script should be scheduled to run hourly on PythonAnywhere:
1. Go to PythonAnywhere Dashboard
2. Click "Tasks" tab
3. Add a scheduled task with this command:
   python /home/yourusername/PDF-Editor/cleanup.py

The script will:
- Scan the instance/uploads/ directory
- Check each session folder's .timestamp file
- Delete folders older than 2 hours
"""
import os
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta


# Configuration
UPLOAD_DIR = Path(__file__).parent / 'instance' / 'uploads'
MAX_AGE_HOURS = 2  # Delete sessions older than this
DRY_RUN = False  # Set to True to test without deleting


def get_folder_age(folder_path):
    """Get the age of a folder based on its .timestamp file"""
    timestamp_file = folder_path / '.timestamp'
    
    if not timestamp_file.exists():
        # If no timestamp file, use folder creation time
        return time.time() - os.path.getctime(folder_path)
    
    try:
        # Read timestamp from file
        timestamp = float(timestamp_file.read_text().strip())
        return time.time() - timestamp
    except (ValueError, IOError):
        # If timestamp is invalid, use folder creation time
        return time.time() - os.path.getctime(folder_path)


def cleanup_old_sessions():
    """Remove session folders older than MAX_AGE_HOURS"""
    if not UPLOAD_DIR.exists():
        print(f"Upload directory does not exist: {UPLOAD_DIR}")
        return
    
    max_age_seconds = MAX_AGE_HOURS * 3600
    deleted_count = 0
    freed_bytes = 0
    
    print(f"Cleanup started at {datetime.now()}")
    print(f"Scanning: {UPLOAD_DIR}")
    print(f"Max age: {MAX_AGE_HOURS} hours")
    print("-" * 60)
    
    # Iterate through session folders
    for session_folder in UPLOAD_DIR.iterdir():
        if not session_folder.is_dir():
            continue
        
        try:
            folder_age = get_folder_age(session_folder)
            folder_age_hours = folder_age / 3600
            
            # Calculate folder size
            folder_size = sum(f.stat().st_size for f in session_folder.rglob('*') if f.is_file())
            
            if folder_age > max_age_seconds:
                print(f"Deleting: {session_folder.name}")
                print(f"  Age: {folder_age_hours:.2f} hours")
                print(f"  Size: {format_bytes(folder_size)}")
                
                if not DRY_RUN:
                    shutil.rmtree(session_folder)
                    deleted_count += 1
                    freed_bytes += folder_size
                else:
                    print("  (DRY RUN - not actually deleted)")
                    deleted_count += 1
                    freed_bytes += folder_size
            else:
                print(f"Keeping: {session_folder.name} (Age: {folder_age_hours:.2f} hours)")
        
        except Exception as e:
            print(f"Error processing {session_folder.name}: {e}")
    
    print("-" * 60)
    print(f"Cleanup completed at {datetime.now()}")
    print(f"Deleted {deleted_count} session(s)")
    print(f"Freed {format_bytes(freed_bytes)} of storage")
    
    if DRY_RUN:
        print("\n*** DRY RUN MODE - No files were actually deleted ***")


def format_bytes(bytes_value):
    """Format bytes into human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"


def create_test_sessions(count=3):
    """Create test session folders with different ages for testing"""
    print("Creating test sessions...")
    
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    import uuid
    
    for i in range(count):
        session_id = str(uuid.uuid4())
        session_folder = UPLOAD_DIR / session_id
        session_folder.mkdir(exist_ok=True)
        
        # Create timestamp file with age
        hours_old = i * 1.5  # 0, 1.5, 3 hours old
        timestamp = time.time() - (hours_old * 3600)
        timestamp_file = session_folder / '.timestamp'
        timestamp_file.write_text(str(timestamp))
        
        # Create a dummy file
        dummy_file = session_folder / f'test_{i}.txt'
        dummy_file.write_text(f'Test session {i}, created {hours_old} hours ago')
        
        print(f"Created test session: {session_id} ({hours_old} hours old)")
    
    print("Test sessions created!")


if __name__ == '__main__':
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            create_test_sessions()
            print("\nNow run 'python cleanup.py --dry-run' to test cleanup")
            sys.exit(0)
        elif sys.argv[1] == '--dry-run':
            DRY_RUN = True
            print("*** DRY RUN MODE - No files will be deleted ***\n")
    
    cleanup_old_sessions()
