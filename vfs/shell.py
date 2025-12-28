import time
from filesystem import FSException


def format_time(timestamp):
    """Format timestamp for display."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def shell(fs):
    """Interactive shell for the virtual filesystem."""
    print("Virtual File System Shell")
    print("Type 'help' for available commands\n")
    
    while True:
        try:
            prompt = f"vfs:{fs.pwd()}$ "
            cmd = input(prompt).strip().split()
            if not cmd:
                continue

            command = cmd[0]
            
            if command == "mkdir":
                if len(cmd) == 2:
                    fs.mkdir(cmd[1])
                    print(f"Directory '{cmd[1]}' created")
                else:
                    print("Usage: mkdir <name>")
                    
            elif command == "create":
                if len(cmd) == 2:
                    fs.create(cmd[1])
                    print(f"File '{cmd[1]}' created")
                else:
                    print("Usage: create <name>")
                    
            elif command == "write":
                if len(cmd) >= 3:
                    # Join all arguments after the path as data
                    data = " ".join(cmd[2:])
                    fs.write(cmd[1], data)
                    print(f"Written {len(data)} bytes to '{cmd[1]}'")
                else:
                    print("Usage: write <path> <data>")
                    
            elif command == "read":
                if len(cmd) == 2:
                    print(fs.read(cmd[1]))
                else:
                    print("Usage: read <path>")
                    
            elif command == "ls":
                items = fs.ls()
                if items:
                    print("\n".join(items))
                else:
                    print("(empty)")
                    
            elif command == "cd":
                if len(cmd) == 2:
                    fs.cd(cmd[1])
                else:
                    print("Usage: cd <path>")
                    
            elif command == "rm":
                if len(cmd) == 3 and cmd[1] == "-r":
                    fs.rm(cmd[2], recursive=True)
                    print(f"Removed '{cmd[2]}' recursively")
                elif len(cmd) == 2:
                    fs.rm(cmd[1])
                    print(f"Removed '{cmd[1]}'")
                else:
                    print("Usage: rm [-r] <path>")
                    
            elif command == "pwd":
                print(fs.pwd())
                
            elif command == "stat":
                if len(cmd) == 2:
                    stats = fs.stat(cmd[1])
                    print(f"Name: {stats['name']}")
                    print(f"Type: {stats['type']}")
                    print(f"Size: {stats['size']} bytes")
                    print(f"Blocks: {stats['blocks']}")
                    print(f"Created: {format_time(stats['created'])}")
                    print(f"Modified: {format_time(stats['modified'])}")
                    print(f"Permissions: {stats['permissions']}")
                else:
                    print("Usage: stat <path>")
                    
            elif command == "du":
                usage = fs.du()
                print("Disk Usage:")
                print(f"  Inodes: {usage['used_inodes']}/{usage['total_inodes']} used "
                      f"({usage['free_inodes']} free)")
                print(f"  Blocks: {usage['used_blocks']}/{usage['total_blocks']} used "
                      f"({usage['free_blocks']} free)")
                print(f"  Block size: {usage['block_size']} bytes")
                total_space = usage['total_blocks'] * usage['block_size']
                used_space = usage['used_blocks'] * usage['block_size']
                print(f"  Total space: {total_space} bytes")
                print(f"  Used space: {used_space} bytes")
                print(f"  Free space: {total_space - used_space} bytes")
                
            elif command == "help":
                print("\nAvailable commands:")
                print("  mkdir <name>        - Create a directory")
                print("  create <name>       - Create a file")
                print("  write <path> <data> - Write data to a file")
                print("  read <path>         - Read file contents")
                print("  ls                  - List directory contents")
                print("  cd <path>           - Change directory")
                print("  rm [-r] <path>      - Remove file/directory")
                print("  pwd                 - Print working directory")
                print("  stat <path>         - Show file/directory statistics")
                print("  du                  - Show disk usage")
                print("  help                - Show this help message")
                print("  exit                - Exit the shell")
                print()
                
            elif command == "exit":
                break
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            print("\nExiting...")
            break
        except FSException as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
