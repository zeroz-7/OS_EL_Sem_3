from typing import List


class SuperBlock:
    """Manages filesystem metadata: inode and block allocation."""
    
    def __init__(self, max_inodes: int = 64, max_blocks: int = 256, block_size: int = 32):
        self.max_inodes = max_inodes
        self.max_blocks = max_blocks
        self.free_inodes: List[bool] = [True] * max_inodes
        self.free_blocks: List[bool] = [True] * max_blocks
        self.block_size = block_size

    def alloc_inode(self) -> int:
        """Allocate a free inode. Raises RuntimeError if none available."""
        for i in range(self.max_inodes):
            if self.free_inodes[i]:
                self.free_inodes[i] = False
                return i
        raise RuntimeError("No free inodes available")

    def free_inode(self, i: int) -> None:
        """Free an inode."""
        if 0 <= i < self.max_inodes:
            self.free_inodes[i] = True

    def alloc_block(self) -> int:
        """Allocate a free block. Raises RuntimeError if none available."""
        for i in range(self.max_blocks):
            if self.free_blocks[i]:
                self.free_blocks[i] = False
                return i
        raise RuntimeError("No free blocks available")

    def free_block(self, i: int) -> None:
        """Free a block."""
        if 0 <= i < self.max_blocks:
            self.free_blocks[i] = True
    
    def get_free_inode_count(self) -> int:
        """Return the number of free inodes."""
        return sum(self.free_inodes)
    
    def get_free_block_count(self) -> int:
        """Return the number of free blocks."""
        return sum(self.free_blocks)
