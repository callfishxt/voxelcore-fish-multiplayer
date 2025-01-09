import time

class ServerTime:
    def __init__(self,set_time,changes,config):
        self.config = config
        self.changes = changes

        self.set_time_func:function = set_time
        self.start_time = time.time() - config.start_time
        self.uptime_seconds = 0
        self.time_until_update = self.config.time_sync 
        self.time_until_auto_save = self.config.auto_save_time

    def uptime(self):
        while True:
            self.current_time = time.time()
            self.uptime_seconds = self.current_time - self.start_time
            
            if self.uptime_seconds >= 1440:
                self.start_time = self.current_time  

            if self.time_until_update <= 0:
                self.set_time_func(int(self.uptime_seconds))
                self.time_until_update = 60 
            else:
                self.time_until_update -= 1 

            if self.config.auto_save == True:
                if self.time_until_auto_save <= 0:
                    self.changes.save_changes()
                    print("changes were saved!")
                    self.time_until_auto_save = self.config.auto_save_time
                else:
                    self.time_until_auto_save -= 1


            #print(f'Uptime: {self.uptime_seconds:.2f} seconds, Time until next update: {self.time_until_update}') для дебажинга
            time.sleep(1)