import tomllib

class Config:
    def __init__(self):
        self.address:str = '0.0.0.0'
        self.port:int = 12345
        self.saving_commands:list = ["bp","bb"]
        self.auto_save:bool = False
        self.auto_save_time:int = 90
        self.time_sync:int = 30
        self.start_time:int = 640
        self.white_list:bool = False
        self.allowed_ips:list = ["127.0.0.1"]
        self.allowed_content_packs:list = ["base:0.25","fmp:1.9"]
        self.optional_content_packs:list = ["fishcones:0.1"]
        self.world_generator:str = "Demo"
        self.world_seed:str = "123"
        self.ops:list = ["127.0.0.1"]

        self.file_name:str = "server_config.toml"
        

    def load(self):
        data = tomllib.load(open(self.file_name,"rb"))

        if "connection" in data:
            if "address" in data["connection"]:
                self.address = data["connection"]["address"]
            if "port" in data["connection"]:
                self.port = data["connection"]["port"]

        if "changes" in data:
            if "saving-commands" in data["changes"]:
                self.saving_commands = data["changes"]["saving-commands"]
            if "auto-save" in data["changes"]:
                self.auto_save = data["changes"]["auto-save"]
            if "auto-save-time" in data["changes"]:
                self.auto_save_time = data["changes"]["auto-save-time"]

        if "time" in data:
            if "time-sync" in data["time"]:
                self.time_sync = data["time"]["time-sync"]
            if "start-time" in data["time"]:
                self.start_time = data["time"]["start-time"]

        if "white-list" in data:
            if "white-list" in data["white-list"]:
                self.white_list = data["white-list"]["white-list"]
            if "allowed-ips" in data["white-list"]:
                self.allowed_ips = data["white-list"]["allowed-ips"]

        if "permissions" in data:
            if "ops" in data["permissions"]:
                self.ops = data["permissions"]["ops"]
        
        if "content-packs" in data:
            if "allowed" in data["content-packs"]:
                self.allowed_content_packs = data["content-packs"]["allowed"]
            if "optional" in data["content-packs"]:
                self.optional_content_packs = data["content-packs"]["optional"]
        
        if "world" in data:
            if "generator" in data["world"]:
                self.world_generator = data["world"]["generator"]
            if "seed" in data["world"]:
                self.world_seed = str(data["world"]["seed"])
