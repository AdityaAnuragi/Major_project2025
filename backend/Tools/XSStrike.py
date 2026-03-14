from copy import deepcopy

XSSTRIKE_PATH = "vendor/XSStrike/xsstrike.py"


class XSStrike:
    __mapper = {
        # value-based attributes
        "url":               lambda value: f"-u {value}",
        "data":              lambda value: f"--data {value}",
        "encode":            lambda value: f"-e {value}",
        "timeout":           lambda value: f"--timeout {value}",
        "seeds":             lambda value: f"--seeds {value}",
        "file":              lambda value: f"-f {value}",
        "level":             lambda value: f"-l {value}",
        "headers":           lambda value: f"--headers {value}",
        "threads":           lambda value: f"-t {value}",
        "delay":             lambda value: f"-d {value}",
        "console_log_level": lambda value: f"--console-log-level {value}",
        "file_log_level":    lambda value: f"--file-log-level {value}",
        "log_file":          lambda value: f"--log-file {value}",

        # flag-only attributes (value is ignored)
        "fuzzer":            lambda value: "--fuzzer",
        "update":            lambda value: "--update",
        "proxy":             lambda value: "--proxy",
        "crawl":             lambda value: "--crawl",
        "json":              lambda value: "--json",
        "path":              lambda value: "--path",
        "skip":              lambda value: "--skip",
        "skip_dom":          lambda value: "--skip-dom",
        "blind":             lambda value: "--blind",
    }

    def __init__(self):
        self.__command = ["python", XSSTRIKE_PATH]

    def addAttribute(self, attribute, value=''):
        if attribute not in self.__class__.__mapper:
            print("ABSENT, attribute not yet mapped")
            return

        fragment = self.__class__.__mapper[attribute](value)
        print(f"PRESENT, adding {fragment} to the command")
        self.__command.extend(fragment.split())

    def getCommand(self):
        return deepcopy(self.__command)

    def getCommandString(self):
        return " ".join(self.__command)
