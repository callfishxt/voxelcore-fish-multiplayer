import sys,time
class Commands_Handler:
    def __init__(self,changes,server_time):
        self.command:str
        self.changes = changes
        self.server_time = server_time
    
    def execute(self,command,*args):
        match command:
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
            case "time":
                _time = self.server_time.current_time
                self.server_time.start_time = _time + float(args[0][0])
                self.server_time.set_time_func(self.server_time.start_time - _time)
                print(f"Set time to {self.server_time.start_time - _time}")


                    
                    
