import json

class ServerConfig:
    def __init__(self, name, displayName, folder, launchCmd, start, stopCmd, startedLine) -> None:
        self.name = name
        self.displayName = displayName
        self.folder = folder
        self.launchCmd =launchCmd
        self.start = start
        self.stopCmd = stopCmd
        self.startedLine = startedLine

    @classmethod
    def getFromDict(cls, dict):
        start = dict["start"] if "start" in dict else True
        stopCmd = dict["stopCmd"] if "stopCmd" in dict else "/stop"
        startedLine = dict["startedLine"] if "startedLine" in dict else r"\[\d+:\d+:\d+\] \[Server thread\/INFO\]: Maintenance mode is .*"
        return cls(dict["name"], dict["displayName"], dict["folder"], dict["launchCmd"], start, stopCmd, startedLine)

def getServerConfigs(filename) -> 'list[ServerConfig]':
    with open(filename, "r") as file:
            data = json.load(file)
    servers = []
    for item in data:
         servers.append(ServerConfig.getFromDict(item))
    return servers