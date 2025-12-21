class SuperBlock:
    def __init__(self, max_inodes=64, max_blocks=256):
        self.max_inodes = max_inodes
        self.max_blocks = max_blocks
        self.free_inodes = [True] * max_inodes
        self.free_blocks = [True] * max_blocks
        self.block_size = 32

    def alloc_inode(self):
        for i in range(self.max_inodes):
            if self.free_inodes[i]:
                self.free_inodes[i] = False
                return i
        raise RuntimeError("No free inodes")

    def free_inode(self, i):
        self.free_inodes[i] = True

    def alloc_block(self):
        for i in range(self.max_blocks):
            if self.free_blocks[i]:
                self.free_blocks[i] = False
                return i
        raise RuntimeError("No free blocks")

    def free_block(self, i):
        self.free_blocks[i] = True
