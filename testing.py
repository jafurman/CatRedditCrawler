import random

string = "The goal of /r/Movies is to provide an inclusive place for discussions…"


def catLike(description):
    newString = ""
    for letter in description:
        randomChance = random.randint(0,30)
        if randomChance == 15 and letter == " ":
            newString += " :3 "
        if randomChance == 20 and letter == " ":
            newString += " >:0 "
        if randomChance == 25 and letter == " ":
            newString += " *lick lick* "
        if randomChance == 5 and letter == " ":
            newString += " HISSSSSSSSSS...  "
        newString += letter
        if letter == "m":
            randNum = random.randint(0, 3)
            if randNum == 2:
                newString += "oeow"
        if letter == "p":
            newString += "rr"

    return newString

printDis = catLike(string)

print(printDis)