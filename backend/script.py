from Tools.Ffuf import Ffuf

ffuf = Ffuf()
ffuf.addAttribute("timeout", 10)
ffuf.addAttribute("threads", 10)
ffuf.addAttribute("url", "http://demo.testfire.net/FUZZ")
ffuf.addAttribute("wordlist", "words.txt")

print(ffuf.getCommandString())



