"""
🅃🄷🄴 🄲🄷🄰🅄🄷🄰🄽 🅃🄴🄲🄷🄽🄾🄻🄾🄶🅈 🄲🄾🄼🄿🄰🄽🅈 🄸🄽🄲.
CREATED BY: LAKSHYA CHAUHAN @LUCKY1106

USAGE:

[GRADE (PERCENTAGE, NOT INCLUDING PERCENT '%' CHARACTER)]:

OPTIONS (IN ORDER OF APPEARANCE):

...+=[ACTUAL GRADE]
...--[SIMULATED GRADE]

"""

def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

f = open("weights.txt", "r")
weights = f.readlines()
origin_weights = weights
weights = unique(weights)
f.close()

weight_values = []
total = 0

wrong_totals = []

totals = []
eachs = []
final = []

sim_totals = []

print()

for weight in weights:
    arg = int(input("Enter the weighting for " + weight.strip() + ": "))
    total += arg
    weight_values.append(arg)
    wrong_totals.append(0)
    totals.append(0)
    sim_totals.append(0)
    eachs.append(0)
    final.append(0)

if total != 100:
    print("\nERROR: Total weighting must be 100")
    exit()

f = open("grades.txt", "r")
grades = f.readlines()

count = 0

for grade in grades:
    if ("--" in grade) and (not ("+=" in grade)):
        grade = grade.split("--")

        sim_totals[weights.index(origin_weights[count])] += float(grade[1].strip())
        wrong_totals[weights.index(origin_weights[count])] += float(grade[0].strip())
        totals[weights.index(origin_weights[count])] += float(grade[0].strip())
        eachs[weights.index(origin_weights[count])] += 1
        final[weights.index(origin_weights[count])] = weight_values[weights.index(origin_weights[count])]
    elif ("+=" in grade) and (not ("--" in grade)):
        grade = grade.split("+=")

        sim_totals[weights.index(origin_weights[count])] += float(grade[1].strip())
        wrong_totals[weights.index(origin_weights[count])] += float(grade[0].strip())
        totals[weights.index(origin_weights[count])] += float(grade[1].strip())
        eachs[weights.index(origin_weights[count])] += 1
        final[weights.index(origin_weights[count])] = weight_values[weights.index(origin_weights[count])]
    elif ("+=" in grade) and ("--" in grade):
        grade = grade.split("+=")

        wrong_totals[weights.index(origin_weights[count])] += float(grade[0].strip())

        grade[1] = grade[1].split("--")

        totals[weights.index(origin_weights[count])] += float(grade[1][0].strip())
        sim_totals[weights.index(origin_weights[count])] += float(grade[1][1].strip())
        eachs[weights.index(origin_weights[count])] += 1
        final[weights.index(origin_weights[count])] = weight_values[weights.index(origin_weights[count])]
    else:
        grade = float(grade.strip())
        wrong_totals[weights.index(origin_weights[count])] += grade
        totals[weights.index(origin_weights[count])] += grade
        sim_totals[weights.index(origin_weights[count])] += grade
        eachs[weights.index(origin_weights[count])] += 1
        final[weights.index(origin_weights[count])] = weight_values[weights.index(origin_weights[count])]
    
    count += 1

wrongs = 0
earns = 0
sims = 0
denom = 0

f = 0
for total in wrong_totals:
    wrongs += float(int(total / eachs[f]) + float(int(str(float((total / eachs[f])))[3])/10)) * final[f]
    denom += final[f]
    f += 1

f = 0
for total in totals:
    earns += float(int(total / eachs[f]) + float(int(str(float((total / eachs[f])))[3])/10)) * final[f]
    f += 1

f = 0
for total in sim_totals:
    sims += float(int(total / eachs[f]) + float(int(str(float((total / eachs[f])))[3])/10)) * final[f]
    f += 1

print("\nWrong: " + str(round((wrongs/denom), 1)) + "0%")
print("\nEarned: " + str(round((earns/denom), 1)) + "0%")
print("\nSimulation: " + str(round((sims/denom), 1)) + "0%\n")