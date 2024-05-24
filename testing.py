import time
import colorama
from colorama import Fore, Back, Style

class EnhanceDialogue:

    def __init__(self,text:str,speed=0.1) -> None:
        self.text = text
        self.speed = speed

        self.print_input()
    
    def print_input(self):
        parsed = ""
        colours = []

        i = 0
        flag = False
        while i != len(self.text):
            if flag:
                if self.text[i] == "m":
                    flag = False
                parsed += "2"
                colours[-1][0] += self.text[i]
                colours[-1][1].append(i)

            else:
                if self.text[i] == '\x1b':
                    parsed += "1"
                    colours.append(['\x1b', [i]])
                    flag = True

                else:
                    parsed += "0"
            i += 1  

        col = ""
        style = ""
        for i in range(len(self.text)):
            if colours:
                for c in colours:
                    if i in c[1]:
                        if len(c[0]) == 5:
                            col = c[0]
                        elif len(c[0]) == 4:
                            style = c[0]
            if parsed[i] == "0":
                print(col + style + self.text[i], end="", sep="", flush=True)
                time.sleep(self.speed)
        print()

 

colorama.init(autoreset=True)
# from scratch_8 import EnhanceDialogue

EnhanceDialogue(f"{Fore.RED} Text {Fore.BLUE + Style.BRIGHT} !!!")
EnhanceDialogue(f"{Fore.MAGENTA}What is your name?")
name = input(">>> ")
print(f"{Fore.CYAN}Good luck {name}!\n")

EnhanceDialogue(f"{Fore.RED}1.abandoned hospital{Fore.RESET}, {Fore.GREEN}2.forest{Fore.RESET}\n{Fore.RED}[1]{Fore.RESET},{Fore.GREEN}[2]{Fore.RESET}")
choice = input(">>> ")
if choice == "1":
    EnhanceDialogue("You chose abandoned hospital.\n")
    EnhanceDialogue(f"You walk into the abandoned hospital and {Fore.LIGHTRED_EX}'shiverr'")
    EnhanceDialogue(f"Do you explore the {Fore.LIGHTRED_EX}1.hospital{Fore.RESET} or 2.quit?\n{Fore.LIGHTRED_EX}[1]{Fore.RESET}, [2]")
    choice = input(">>> ")
    if choice == "1":
        EnhanceDialogue("\nalright. you win gg")
    elif choice == "2":
        EnhanceDialogue("\nyou lose")
        exit()


elif choice == "2":
    EnhanceDialogue("you chose forest\n ")
    EnhanceDialogue(f"Do you 1.wander around the {Back.RED}forest{colorama.Back.RESET} or 2.quit?\n {Back.RED}[1]{Fore.RESET},[2]")
    choice = input(">>> ")
    if choice == "1":
        EnhanceDialogue("\nalright you kinda win gg")
    elif choice == "2":
        EnhanceDialogue("\nyou lose")
        exit()

print(Fore.RESET)