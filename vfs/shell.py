from filesystem import FSException


def shell(fs):
    while True:
        try:
            prompt = f"vfs:{fs.pwd()}$ "
            cmd = input(prompt).strip().split()
            if not cmd:
                continue

            if cmd[0] == "mkdir":
                if len(cmd) == 2:
                    fs.mkdir(cmd[1])
                else:
                    print("Usage: mkdir <path>")
            elif cmd[0] == "create":
                if len(cmd) == 2:
                    fs.create(cmd[1])
                else:
                    print("Usage: create <path>")
            elif cmd[0] == "write":
                if len(cmd) == 3:
                    fs.write(cmd[1], cmd[2])
                else:
                    print("Usage: write <path> <data>")
            elif cmd[0] == "read":
                if len(cmd) == 2:
                    print(fs.read(cmd[1]))
                else:
                    print("Usage: read <path>")
            elif cmd[0] == "ls":
                print(" ".join(fs.ls()))
            elif cmd[0] == "cd":
                if len(cmd) == 2:
                    fs.cd(cmd[1])
                else:
                    print("Usage: cd <path>")
            elif cmd[0] == "rm":
                if len(cmd) == 3 and cmd[1] == "-r":
                    fs.rm(cmd[2], recursive=True)
                elif len(cmd) == 2:
                    fs.rm(cmd[1])
                else:
                    print("Usage: rm [-r] <path>")
            elif cmd[0] == "pwd":
                print(fs.pwd())
            elif cmd[0] == "exit":
                break
            else:
                print("Unknown command")

        except FSException as e:
            print("Error:", e)
