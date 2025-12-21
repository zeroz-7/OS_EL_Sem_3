class Inode:
    def __init__(self, name, inode_type, parent=None):
        self.name = name
        self.type = inode_type      # "file" or "dir"
        self.parent = parent        # parent inode id
        self.size = 0
        self.blocks = []            # data block indices
        self.children = {}          # name -> inode id (dirs only)
