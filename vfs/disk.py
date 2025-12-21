class Disk:
    def __init__(self, superblock):
        self.superblock = superblock
        self.inodes = [None] * superblock.max_inodes
        self.blocks = [""] * superblock.max_blocks

    def read_inode(self, inode_id):
        return self.inodes[inode_id]

    def write_inode(self, inode_id, inode):
        self.inodes[inode_id] = inode

    def read_block(self, block_id):
        return self.blocks[block_id]

    def write_block(self, block_id, data):
        self.blocks[block_id] = data
