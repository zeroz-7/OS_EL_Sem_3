import time
from typing import List, Optional
from inode import Inode
from disk import Disk


class FSException(Exception):
    """Base exception for filesystem errors."""
    pass


class FileNotFound(FSException):
    """Raised when a file or directory is not found."""
    pass


class FileExists(FSException):
    """Raised when trying to create a file that already exists."""
    pass


class NotADirectory(FSException):
    """Raised when a directory operation is attempted on a file."""
    pass


class IsADirectory(FSException):
    """Raised when a file operation is attempted on a directory."""
    pass


class DirectoryNotEmpty(FSException):
    """Raised when trying to remove a non-empty directory."""
    pass


class DiskFull(FSException):
    """Raised when disk is full."""
    pass


class FileSystem:
    """Main filesystem interface providing file and directory operations."""
    
    def __init__(self, disk: Disk):
        self.disk = disk
        self.cwd = 0  # root inode id

    def _resolve(self, path: str) -> int:
        """Resolve a path to an inode ID. Supports absolute and relative paths."""
        if path == "/":
            return 0

        parts = path.strip().split("/")
        curr = 0 if path.startswith("/") else self.cwd

        for part in parts:
            if part in ("", "."):
                continue

            if part == "..":
                curr = self.disk.read_inode(curr).parent or 0
                continue

            inode = self.disk.read_inode(curr)
            if inode.type != "dir":
                raise NotADirectory(f"{inode.name} is not a directory")

            if part not in inode.children:
                raise FileNotFound(f"No such file or directory: {path}")

            curr = inode.children[part]

        return curr

    def mkdir(self, name: str) -> None:
        """Create a new directory in the current working directory."""
        parent = self.disk.read_inode(self.cwd)

        if parent.type != "dir":
            raise NotADirectory("Current location is not a directory")
        
        if "/" in name or name in ("", ".", ".."):
            raise FSException("Invalid name")

        if name in parent.children:
            raise FileExists(f"Directory already exists: {name}")

        try:
            inode_id = self.disk.superblock.alloc_inode()
        except RuntimeError:
            raise DiskFull("No free inodes available")

        inode = Inode(name, "dir", self.cwd)

        parent.children[name] = inode_id
        self.disk.write_inode(inode_id, inode)
        self.disk.write_inode(self.cwd, parent)  # Write parent back

    def ls(self) -> List[str]:
        """List contents of the current directory."""
        inode = self.disk.read_inode(self.cwd)
        if inode.type != "dir":
            raise NotADirectory("Not a directory")
        return list(inode.children.keys())

    def cd(self, path: str) -> None:
        """Change the current working directory."""
        inode_id = self._resolve(path)
        inode = self.disk.read_inode(inode_id)

        if inode.type != "dir":
            raise NotADirectory("Not a directory")

        self.cwd = inode_id
    
    def create(self, name: str) -> None:
        """Create a new file in the current working directory."""
        parent = self.disk.read_inode(self.cwd)
        if parent.type != "dir":
            raise NotADirectory("Not a directory")
        if "/" in name or name in ("", ".", ".."):
            raise FSException("Invalid name")
        if name in parent.children:
            raise FileExists(f"File already exists: {name}")

        try:
            inode_id = self.disk.superblock.alloc_inode()
        except RuntimeError:
            raise DiskFull("No free inodes available")

        inode = Inode(name, "file", self.cwd)

        parent.children[name] = inode_id
        self.disk.write_inode(inode_id, inode)
        self.disk.write_inode(self.cwd, parent)  # Write parent back

    def write(self, name: str, data: str) -> None:
        """Write data to a file, overwriting existing content."""
        inode_id = self._resolve(name)
        inode = self.disk.read_inode(inode_id)

        if inode.type != "file":
            raise IsADirectory("Cannot write to a directory")

        # Free existing blocks
        for b in inode.blocks:
            self.disk.superblock.free_block(b)
        inode.blocks.clear()

        # Allocate and write new blocks
        sb = self.disk.superblock
        blocks_needed = (len(data) + sb.block_size - 1) // sb.block_size
        
        if blocks_needed > sb.get_free_block_count():
            raise DiskFull("Not enough free blocks to write file")
        
        for i in range(0, len(data), sb.block_size):
            try:
                block = sb.alloc_block()
            except RuntimeError:
                # Free already allocated blocks on error
                for b in inode.blocks:
                    self.disk.superblock.free_block(b)
                inode.blocks.clear()
                raise DiskFull("No free blocks available")
            
            chunk = data[i:i+sb.block_size]
            self.disk.write_block(block, chunk)
            inode.blocks.append(block)

        inode.size = len(data)
        inode.modified = time.time()
        self.disk.write_inode(inode_id, inode)  # Write inode back after updating

    def read(self, name: str) -> str:
        """Read the contents of a file."""
        inode_id = self._resolve(name)
        inode = self.disk.read_inode(inode_id)

        if inode.type != "file":
            raise IsADirectory("Cannot read a directory")

        content = ""
        for b in inode.blocks:
            content += self.disk.read_block(b)
        return content

    def pwd(self) -> str:
        """Get the current working directory path."""
        parts = []
        curr = self.cwd
        while curr != 0:
            inode = self.disk.read_inode(curr)
            parts.append(inode.name)
            curr = inode.parent
        return "/" + "/".join(reversed(parts))
    
    def stat(self, path: str) -> dict:
        """Get file/directory statistics."""
        inode_id = self._resolve(path)
        inode = self.disk.read_inode(inode_id)
        return {
            'name': inode.name,
            'type': inode.type,
            'size': inode.size,
            'blocks': len(inode.blocks),
            'created': inode.created,
            'modified': inode.modified,
            'permissions': oct(inode.permissions)
        }
    
    def du(self) -> dict:
        """Get disk usage statistics."""
        return {
            'total_inodes': self.disk.superblock.max_inodes,
            'free_inodes': self.disk.superblock.get_free_inode_count(),
            'used_inodes': self.disk.superblock.max_inodes - self.disk.superblock.get_free_inode_count(),
            'total_blocks': self.disk.superblock.max_blocks,
            'free_blocks': self.disk.superblock.get_free_block_count(),
            'used_blocks': self.disk.superblock.max_blocks - self.disk.superblock.get_free_block_count(),
            'block_size': self.disk.superblock.block_size
        }

    def _rm_recursive(self, inode_id: int) -> None:
        inode = self.disk.read_inode(inode_id)

        # If directory → recursively delete children
        if inode.type == "dir":
            for child_id in list(inode.children.values()):
                self._rm_recursive(child_id)

        # Free file blocks
        for b in inode.blocks:
            self.disk.superblock.free_block(b)

        # Remove from parent directory
        if inode.parent is not None:
            parent = self.disk.read_inode(inode.parent)
            if parent and inode.name in parent.children:
                del parent.children[inode.name]
                self.disk.write_inode(inode.parent, parent)  # Write parent back

        # Free inode itself
        self.disk.superblock.free_inode(inode_id)
        self.disk.write_inode(inode_id, None)

    def rm(self, path: str, recursive: bool = False) -> None:
        """Remove a file or directory."""
        inode_id = self._resolve(path)
        if inode_id == 0 or path == "/":
            raise FSException("Cannot remove root directory")

        inode = self.disk.read_inode(inode_id)

        if inode.type == "dir" and inode.children and not recursive:
            raise DirectoryNotEmpty("Directory not empty")

        if recursive:
            self._rm_recursive(inode_id)
        else:
            for b in inode.blocks:
                self.disk.superblock.free_block(b)

            parent = self.disk.read_inode(inode.parent)
            if parent:
                del parent.children[inode.name]
                self.disk.write_inode(inode.parent, parent)  # Write parent back

            self.disk.superblock.free_inode(inode_id)
            self.disk.write_inode(inode_id, None)
