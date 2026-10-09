import subprocess
import os
import sys

def build():
    print("Starting build process for BMI Label Generator...")
    
    # Ensure we are in the correct directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # First, try to kill any running instance of the app so we don't get permission errors
    print("Closing any running instances of the app to avoid file lock errors...")
    if sys.platform.startswith("win"):
        try:
            subprocess.run(["taskkill", "/F", "/IM", "label_app.exe"], capture_output=True)
        except Exception:
            pass

    # Backup existing database in dist if it exists
    dist_db = os.path.join(base_dir, "dist", "label_app", "label_history.db")
    backup_db = os.path.join(base_dir, "dist_label_history_backup.db")
    if os.path.exists(dist_db):
        import shutil
        shutil.copy2(dist_db, backup_db)

    # Run PyInstaller
    print("Running PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "--noconfirm", "label_app.spec"])
        
        # Copy the labels folder to the dist directory
        import shutil
        src_labels = os.path.join(base_dir, "labels")
        dst_labels = os.path.join(base_dir, "dist", "label_app", "labels")
        if os.path.exists(src_labels):
            if os.path.exists(dst_labels):
                shutil.rmtree(dst_labels)
            shutil.copytree(src_labels, dst_labels)

        # Restore / copy database
        target_db = os.path.join(base_dir, "dist", "label_app", "label_history.db")
        if os.path.exists(backup_db):
            shutil.copy2(backup_db, target_db)
            os.remove(backup_db)
        elif os.path.exists(os.path.join(base_dir, "label_history.db")):
            shutil.copy2(os.path.join(base_dir, "label_history.db"), target_db)

        # Copy config.json
        src_cfg = os.path.join(base_dir, "config.json")
        dst_cfg = os.path.join(base_dir, "dist", "label_app", "config.json")
        if os.path.exists(src_cfg):
            shutil.copy2(src_cfg, dst_cfg)
            
        print("\nSUCCESS! The executable has been built in the 'dist' folder.")
        print(f"Path: {os.path.join(base_dir, 'dist', 'label_app', 'label_app.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: PyInstaller failed with exit code {e.returncode}")
    except FileNotFoundError:
        print("\nERROR: PyInstaller not found. Ensure it is installed with 'pip install pyinstaller'.")

if __name__ == "__main__":
    build()
