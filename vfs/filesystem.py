from inode import Inode

class FSException(Exception):
    pass

class FileNotFound(FSException):
    pass

class FileExists(FSException):
    pass

class NotADirectory(FSException):
    pass

class IsADirectory(FSException):
    pass

class DirectoryNotEmpty(FSException):
    pass


class FileSystem:
    def __init__(self, disk):
        self.disk = disk
        self.cwd = 0  # root inode id

    def _resolve(self, path):
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

    def mkdir(self, name):
        parent = self.disk.read_inode(self.cwd)

        if parent.type != "dir":
            raise NotADirectory("Current location is not a directory")
        
        if "/" in name or name in ("", ".", ".."):
            raise FSException("Invalid name")

        if name in parent.children:
            raise FileExists(f"Directory already exists: {name}")

        inode_id = self.disk.superblock.alloc_inode()
        inode = Inode(name, "dir", self.cwd)

        parent.children[name] = inode_id
        self.disk.write_inode(inode_id, inode)

    def ls(self):
        inode = self.disk.read_inode(self.cwd)
        if inode.type != "dir":
            raise NotADirectory("Not a directory")
        return list(inode.children.keys())

    def cd(self, path):
        inode_id = self._resolve(path)
        inode = self.disk.read_inode(inode_id)

        if inode.type != "dir":
            raise NotADirectory("Not a directory")

        self.cwd = inode_id
    
    def create(self, name):
        parent = self.disk.read_inode(self.cwd)
        if parent.type != "dir":
            raise NotADirectory("Not a directory")
        if "/" in name or name in ("", ".", ".."):
            raise FSException("Invalid name")
        if name in parent.children:
            raise FileExists(f"File already exists: {name}")

        inode_id = self.disk.superblock.alloc_inode()
        inode = Inode(name, "file", self.cwd)

        parent.children[name] = inode_id
        self.disk.write_inode(inode_id, inode)

    def write(self, name, data):
        inode_id = self._resolve(name)
        inode = self.disk.read_inode(inode_id)

        if inode.type != "file":
            raise IsADirectory("Cannot write to a directory")

        for b in inode.blocks:
            self.disk.superblock.free_block(b)
        inode.blocks.clear()

        sb = self.disk.superblock
        for i in range(0, len(data), sb.block_size):
            block = sb.alloc_block()
            chunk = data[i:i+sb.block_size]
            self.disk.write_block(block, chunk)
            inode.blocks.append(block)

        inode.size = len(data)

    def read(self, name):
        inode_id = self._resolve(name)
        inode = self.disk.read_inode(inode_id)

        if inode.type != "file":
            raise IsADirectory("Cannot read a directory")

        content = ""
        for b in inode.blocks:
            content += self.disk.read_block(b)
        return content

    def pwd(self):
        parts = []
        curr = self.cwd
        while curr != 0:
            inode = self.disk.read_inode(curr)
            parts.append(inode.name)
            curr = inode.parent
        return "/" + "/".join(reversed(parts))

    def _rm_recursive(self, inode_id):
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

        # Free inode itself
        self.disk.superblock.free_inode(inode_id)
        self.disk.write_inode(inode_id, None)

    def rm(self, path, recursive=False):
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

            self.disk.superblock.free_inode(inode_id)
            self.disk.write_inode(inode_id, None)
