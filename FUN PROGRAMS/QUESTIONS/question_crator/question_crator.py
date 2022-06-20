f = open("questions.txt", "r", encoding="utf8")
questions = f.readlines()
f.close()

# starting line, number of lines, change
x = range(6, 118, 7)

f = open("correct.txt", "w")
content = ""

for n in x:
    content += (questions[n - 1]).strip()
    content += "\n"

f.write(content)
f.close()
print("Program Terminated ... \n")