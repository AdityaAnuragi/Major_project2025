from flask.sansio.scaffold import T_url_defaults
from Tools.Ffuf import Ffuf

import os

command_1 = Ffuf()

target_url = input('Enter the target URL (press ENTER for default value [http://testphp.vulnweb.com/FUZZ]) : ') or 'http://testphp.vulnweb.com/FUZZ'

# value-based attributes
command_1.addAttribute("wordlist", "words.txt")
command_1.addAttribute("target_url", target_url)
command_1.addAttribute("threads", 100)
command_1.addAttribute("match_status", 200)

# flag-only attributes
command_1.addAttribute("follow_redirects")
command_1.addAttribute("ignore_comments")
command_1.addAttribute("non_interactive")
command_1.addAttribute("recursion")

command_1_string_command = command_1.getCommandString()

print(command_1_string_command)

os.system(command_1_string_command)

print("\n\n\n")

command_2 = Ffuf()

command_2.addAttribute("wordlist", "words.txt")
command_2.addAttribute("target_url", target_url)
command_2.addAttribute("threads", 200)

# flag-only attributes
command_2.addAttribute("follow_redirects")
command_2.addAttribute("ignore_comments")
command_2.addAttribute("non_interactive")
command_2.addAttribute("silent_mode")

command_2_string_command = command_2.getCommandString()

print(command_2_string_command)

os.system(command_2_string_command)
