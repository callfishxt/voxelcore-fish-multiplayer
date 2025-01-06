import sys
class Commands_Handler:
    def __init__(self,changes):
        self.command:str
        self.changes = changes
    
    def start(self):
        while True:
            self.command = input("")
            match self.command.split()[0]:
                case "exit":
                    self.changes.save_changes()
                    print("Changes successfully saved\n Closing...")
                    sys.exit(0)
                case "save":
                    self.changes.save_changes()
                    print("Changes successfully saved")
                case "load":
                    self.changes.changes = self.changes.read_changes()
                    print("Changes successfully restored from file")
                case "rageexit":
                    print(" Closing...")
                    sys.exit(0)
                case "clear":
                    self.changes.changes = ""
                    
                    
