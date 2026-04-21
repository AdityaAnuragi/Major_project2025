from copy import deepcopy

SQLMAP_PATH = "vendor/sqlmap/sqlmap.py"


class Sqlmap:
    __mapper = {
        # value-based attributes
        "url":       lambda value: f"-u {value}",
        "urls_file": lambda value: f"-m {value}",
        "level":     lambda value: f"--level={value}",
        "risk":      lambda value: f"--risk={value}",
        "cookie":    lambda value: f'--cookie "{value}"',
        "headers":   lambda value: f'--headers "{value}"',

        # flag-only attributes (value is ignored)
        "time_sec":  lambda value: f"--time-sec={value}",
        "technique": lambda value: f"--technique={value}",
        "crawl":     lambda value: f"--crawl={value}",
        "batch":     lambda value: "--batch",
        "forms":     lambda value: "--forms",
    }

    def __init__(self):
        self.__command = ["python", SQLMAP_PATH]

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
