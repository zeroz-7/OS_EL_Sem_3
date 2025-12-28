import time
from typing import Optional, Dict, List


class Inode:
    """Represents a file or directory inode with metadata."""
    
    def __init__(self, name: str, inode_type: str, parent: Optional[int] = None):
        self.name = name
        self.type = inode_type      # "file" or "dir"
        self.parent = parent        # parent inode id
        self.size = 0
        self.blocks: List[int] = []            # data block indices
        self.children: Dict[str, int] = {}     # name -> inode id (dirs only)
        self.created = time.time()
        self.modified = time.time()
        self.permissions = 0o755 if inode_type == "dir" else 0o644
