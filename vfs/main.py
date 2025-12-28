import sys
import os
from superblock import SuperBlock
from disk import Disk
from inode import Inode
from filesystem import FileSystem
from shell import shell

DEFAULT_FS_FILE = "vfs_data.pkl"


def init_filesystem():
    """Initialize a new filesystem."""
    sb = SuperBlock()
    disk = Disk(sb)

    root = Inode("/", "dir")
    disk.write_inode(0, root)
    sb.free_inodes[0] = False

    return FileSystem(disk)


def load_filesystem(filename: str):
    """Load filesystem from file."""
    if not os.path.exists(filename):
        print(f"Filesystem file '{filename}' not found. Creating new filesystem.")
        return init_filesystem()
    
    try:
        sb = SuperBlock()
        disk = Disk(sb)
        disk.load(filename)
        return FileSystem(disk)
    except Exception as e:
        print(f"Error loading filesystem: {e}")
        print("Creating new filesystem.")
        return init_filesystem()


def main():
    fs_file = DEFAULT_FS_FILE
    if len(sys.argv) > 1:
        fs_file = sys.argv[1]
    
    # Load or create filesystem
    fs = load_filesystem(fs_file)
    
    # Store filename for saving
    fs._fs_file = fs_file
    
    try:
        shell(fs)
    finally:
        # Save filesystem on exit
        try:
            fs.disk.save(fs_file)
            print(f"\nFilesystem saved to '{fs_file}'")
        except Exception as e:
            print(f"\nWarning: Could not save filesystem: {e}")


if __name__ == "__main__":
    main()
