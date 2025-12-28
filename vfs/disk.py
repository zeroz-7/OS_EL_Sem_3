import pickle
from typing import Optional, List
from superblock import SuperBlock
from inode import Inode


class Disk:
    """Simulates disk storage for inodes and data blocks."""
    
    def __init__(self, superblock: SuperBlock):
        self.superblock = superblock
        self.inodes: List[Optional[Inode]] = [None] * superblock.max_inodes
        self.blocks: List[str] = [""] * superblock.max_blocks

    def read_inode(self, inode_id: int) -> Optional[Inode]:
        """Read an inode from disk."""
        if not 0 <= inode_id < self.superblock.max_inodes:
            raise IndexError(f"Invalid inode ID: {inode_id}")
        return self.inodes[inode_id]

    def write_inode(self, inode_id: int, inode: Optional[Inode]) -> None:
        """Write an inode to disk."""
        if not 0 <= inode_id < self.superblock.max_inodes:
            raise IndexError(f"Invalid inode ID: {inode_id}")
        self.inodes[inode_id] = inode

    def read_block(self, block_id: int) -> str:
        """Read a data block from disk."""
        if not 0 <= block_id < self.superblock.max_blocks:
            raise IndexError(f"Invalid block ID: {block_id}")
        return self.blocks[block_id]

    def write_block(self, block_id: int, data: str) -> None:
        """Write a data block to disk."""
        if not 0 <= block_id < self.superblock.max_blocks:
            raise IndexError(f"Invalid block ID: {block_id}")
        if len(data) > self.superblock.block_size:
            raise ValueError(f"Data exceeds block size ({self.superblock.block_size})")
        self.blocks[block_id] = data
    
    def save(self, filename: str) -> None:
        """Save the filesystem to a file."""
        with open(filename, 'wb') as f:
            pickle.dump({
                'superblock': self.superblock,
                'inodes': self.inodes,
                'blocks': self.blocks
            }, f)
    
    def load(self, filename: str) -> None:
        """Load the filesystem from a file."""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            self.superblock = data['superblock']
            self.inodes = data['inodes']
            self.blocks = data['blocks']
