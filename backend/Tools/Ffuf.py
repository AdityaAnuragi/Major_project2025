import shlex
from copy import deepcopy

class Ffuf:
    __mapper = {
        # value-based attributes
        "wordlist": lambda value: f"-w {value}:FUZZ",
        "target_url": lambda value: f"-u {value}",
        "threads": lambda value: f"-t {value}",
        "match_status": lambda value: f"-mc {value}",

        # flag-only attributes (value is ignored)
        "follow_redirects": lambda value: "-r",
        "ignore_comments": lambda value: "-ic",
        "non_interactive": lambda value: "-noninteractive",
        "recursion": lambda value: "-recursion",
        "silent_mode": lambda value: "-s",
    }


    def __init__(self):
        self.__command = ["ffuf"]

    def addAttribute(self, attribute, value = ''):
        if attribute not in self.__class__.__mapper:
            print("ABSENT, attribute not yet mapped")
            return

        fragment = self.__class__.__mapper[attribute](value)
        print(f"PRESENT, adding {fragment} to the command")
        self.__command.extend(fragment.split())

    def getCommand(self):
        return deepcopy(self.__command)

    def getCommandString(self):
        quoted_parts = []

        for arg in self.__command:
            quoted = shlex.quote(arg)
            quoted_parts.append(quoted)

        command_string = " ".join(quoted_parts)
        return command_string
