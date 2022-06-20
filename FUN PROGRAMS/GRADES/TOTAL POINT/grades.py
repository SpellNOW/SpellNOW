"""
🅃🄷🄴 🄲🄷🄰🅄🄷🄰🄽 🅃🄴🄲🄷🄽🄾🄻🄾🄶🅈 🄲🄾🄼🄿🄰🄽🅈 🄸🄽🄲.
CREATED BY: LAKSHYA CHAUHAN @LUCKY1106

USAGE:

[ORIGINAL POINTS EARNED]|/|[TOTAL POINTS POSSIBLE]

OPTIONS (IN ORDER OF APPEARANCE):

...+=[ACTUAL EARNED POINTS]
...--[SIMULATED POINTS]

"""

f = open("grades.txt", "r")
grades = f.readlines()
f.close()

given = 0
earned = 0
simulation = 0
total = 0

for grade in grades:
    test = grade.split("|/|")
    if ("--" in test[1]) and (not ("+=" in test[1])):
        given += int(test[0])
        wrong = test[1].split("--")

        earned += int(test[0])
        simulation += int(wrong[1])
        total += int(wrong[0])
    elif ("+=" in test[1]) and (not ("--" in test[1])):
        given += int(test[0])
        wrong = test[1].split("+=")
        
        earned += int(wrong[1])
        simulation += int(wrong[1])
        total += int(wrong[0])
    elif ("+=" in test[1]) and ("--" in test[1]):
        given += int(test[0])
        wrong = test[1].split("+=")
        hard = wrong[1].split("--")
        
        earned += int(hard[0])
        simulation += int(hard[1])
        total += int(wrong[0])
    else:
        given += int(test[0])
        earned += int(test[0])
        simulation += int(test[0])
        total += int(test[1].replace("--", ""))

f.close()
print("\nWrong: " + str(given) + "/" + str(total) + " = " + str(round(((given/total) * 100), 1)) + "0%")
print("\nEarned: " + str(earned) + "/" + str(total) + " = " + str(round(((earned/total) * 100), 1)) + "0%")
print("\nSimulation: " + str(simulation) + "/" + str(total) + " = " + str(round(((simulation/total) * 100), 1)) + "0%\n")