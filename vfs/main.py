from superblock import SuperBlock
from disk import Disk
from inode import Inode
from filesystem import FileSystem
from shell import shell

sb = SuperBlock()
disk = Disk(sb)

root = Inode("/", "dir")
disk.write_inode(0, root)
sb.free_inodes[0] = False

fs = FileSystem(disk)
shell(fs)
