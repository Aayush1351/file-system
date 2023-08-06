import cmd
import datetime

class Node:
    def __init__(self, name, parent=None, is_directory=False):
        self.name = name
        self.parent = parent
        self.is_directory = is_directory
        self.children = {} if is_directory else None
        self.content = "" if not is_directory else None
        self.created_time = datetime.datetime.now() if not is_directory else None
        self.size = 0 if not is_directory else None

    def path(self):
        if self.parent:
            return self.parent.path() + '/' + self.name
        else:
            return self.name

class FileSystem:
    def __init__(self):
        self.root = Node('/', is_directory=True)
        self.current_node = self.root

    def touch(self, name):
        if name in self.current_node.children:
            print("File already exists.")
        else:
            self.current_node.children[name] = Node(name, self.current_node)

    def mkdir(self, name):
        if name in self.current_node.children:
            print("Directory already exists.")
        else:
            self.current_node.children[name] = Node(name, self.current_node, is_directory=True)

    def cd(self, name):
        if name == "..":
            if self.current_node.parent:
                self.current_node = self.current_node.parent
            else:
                print("Already at root directory.")
        elif name in self.current_node.children and self.current_node.children[name].is_directory:
            self.current_node = self.current_node.children[name]
        else:
            print("No such directory.")

    def ls(self):
        for child in self.current_node.children.values():
            if child.is_directory:
                print(child.name + "/")
            else:
                print(f"{child.name}\t{child.size}B\t{child.created_time}")

    def pwd(self):
        print(self.current_node.path())

    def rm(self, name):
        if name in self.current_node.children and not self.current_node.children[name].is_directory:
            del self.current_node.children[name]
        else:
            print("No such file.")

    def rmdir(self, name):
        if name in self.current_node.children and self.current_node.children[name].is_directory:
            del self.current_node.children[name]
        else:
            print("No such directory.")

    def write(self, name, content):
        if name in self.current_node.children and not self.current_node.children[name].is_directory:
            self.current_node.children[name].content = content
            self.current_node.children[name].size = len(content)
        else:
            print("No such file.")

    def read(self, name):
        if name in self.current_node.children and not self.current_node.children[name].is_directory:
            print(self.current_node.children[name].content)
        else:
            print("No such file.")

    def cp(self, src, dest):
        if src in self.current_node.children and not self.current_node.children[src].is_directory:
            if dest in self.current_node.children:
                print("Destination file already exists.")
            else:
                new_file = Node(dest, self.current_node)
                new_file.content = self.current_node.children[src].content
                new_file.size = self.current_node.children[src].size
                self.current_node.children[dest] = new_file
        else:
            print("Source file does not exist.")

    def mv(self, src, dest):
    # split src and dest into path and name
        src_path, src_name = self.split_path(src)
        dest_path, dest_name = self.split_path(dest)
    
    # if the destination is a directory, we keep the source file name
        if dest_name == "":
            dest_name = src_name
        
    # get the node corresponding to the src and dest
        src_node = self.get_node(src_path)
        dest_node = self.get_node(dest_path)
    
        if src_node and dest_node and src_name in src_node.children:
            if dest_name in dest_node.children:
                print("Destination already exists.")
            else:
                # move the file/directory from source to destination
                src_node.children[src_name].name = dest_name
                src_node.children[src_name].parent = dest_node
                dest_node.children[dest_name] = src_node.children[src_name]
                del src_node.children[src_name]
        else:
            print("Source or destination does not exist.")
        
    def split_path(self, path):
        path = path.split('/')
        name = path[-1]
        parent_path = '/'.join(path[:-1]) if len(path) > 1 else None
        return parent_path, name

    def get_node(self, path):
        if path is None:
            return self.current_node
        else:
            node = self.root
            for part in path.split('/'):
                if part in node.children:
                    node = node.children[part]
                else:
                    return None
            return node


class FileSystemShell(cmd.Cmd):
    def __init__(self, file_system):
        super().__init__()
        self.fs = file_system
        self.prompt = '> '

    def do_touch(self, arg):
        self.fs.touch(arg)

    def do_mkdir(self, arg):
        self.fs.mkdir(arg)

    def do_cd(self, arg):
        self.fs.cd(arg)

    def do_ls(self, arg):
        self.fs.ls()

    def do_pwd(self, arg):
        self.fs.pwd()

    def do_rm(self, arg):
        self.fs.rm(arg)

    def do_rmdir(self, arg):
        self.fs.rmdir(arg)

    def do_write(self, arg):
        parts = arg.split(' ', maxsplit=1)
        if len(parts) != 2:
            print("Usage: write <filename> <content>")
        else:
            self.fs.write(parts[0], parts[1])

    def do_read(self, arg):
        self.fs.read(arg)

    def do_cp(self, arg):
        parts = arg.split(' ', maxsplit=1)
        if len(parts) != 2:
            print("Usage: cp <source_file> <destination_file>")
        else:
            self.fs.cp(parts[0], parts[1])

    def do_mv(self, arg):
        parts = arg.split(' ', maxsplit=1)
        if len(parts) != 2:
            print("Usage: mv <source> <destination>")
        else:
            self.fs.mv(parts[0], parts[1])

    def do_exit(self, arg):
        return True

if __name__ == '__main__':
    FileSystemShell(FileSystem()).cmdloop()
