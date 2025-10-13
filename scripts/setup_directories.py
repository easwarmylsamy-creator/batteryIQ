# scripts/setup_directories.py
"""
Setup required directory structure for BatteryIQ
Run this once after cloning the repository
"""
import os

def create_directory_structure():
    """Create all required directories"""
    directories = [
        "data/user_profiles",
        "data/uploads/telemetry",
        "data/uploads/manual",
        "data/test/uploads",
        "logs",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
        
        # Create .gitkeep files to preserve empty directories
        gitkeep_path = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write("")
            print(f"  └─ Added .gitkeep")
    
    print("\n✅ Directory structure setup complete!")


if __name__ == "__main__":
    print("Setting up BatteryIQ directory structure...\n")
    create_directory_structure()