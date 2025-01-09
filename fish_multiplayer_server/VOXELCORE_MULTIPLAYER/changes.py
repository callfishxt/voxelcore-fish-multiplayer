class ChangeManager:
    def __init__(self):
        self.changes = ""

    def add_change(self,line):
        self.changes += line + "\n"
    
    def get_changes(self): return self.changes

    def save_changes(self,file="changes.chs"):
        with open(file,"w+") as f:
            f.write(self.changes)
            f.close()

    def read_changes(self,file="changes.chs"):
        data:str
        with open(file,"r") as f:
             data = f.read()
        return data
    
    def to_list(self):
        List = self.changes.split("\n")
        return List

        