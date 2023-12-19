import json

class ServerConfig:
    def __init__(self, name, displayName, folder, launchCmd) -> None:
        self.name = name
        self.displayName = displayName
        self.folder = folder
        self.launchCmd =launchCmd

    @classmethod
    def getFromDict(cls, dict):
        return cls(dict["name"], dict["displayName"], dict["folder"], dict["launchCmd"])

def getServerConfigs(filename):
    with open(filename, "r") as file:
            data = json.load(file)
    servers = []
    for item in data:
         servers.append(ServerConfig.getFromDict(item))
    return servers