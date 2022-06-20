import random

def key(value, list):
    for i in range(len(list)):
        if list[i] == value:
            return int(i)
    return -1

def turn(list):
    newone = []
    for i in range(len(list)):
        if i == 0:
            newone.append(list[25])
        else:
            newone.append(list[i - 1])
    return newone

def negturn(list):
    newone = []
    for i in range(len(list)):
        if i == 25:
            newone.append(list[0])
        else:
            newone.append(list[i + 1])
    return newone
      
mainfinal = ''

print("\n███████████████████████████████████████████████████████████████████████████████████████████████████████")
print("█░░░░░░░░░░░░░░█░░░░░░██████████░░░░░░█░░░░░░░░░░█░░░░░░░░░░░░░░█░░░░░░██████████░░░░░░█░░░░░░░░░░░░░░█")
print("█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░░░░░░░░░██░░▄▀░░█░░▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░░░░░░░░░░░░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█")
print("█░░▄▀░░░░░░░░░░█░░▄▀▄▀▄▀▄▀▄▀░░██░░▄▀░░█░░░░▄▀░░░░█░░▄▀░░░░░░░░░░█░░▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░░░░░▄▀░░█")
print("█░░▄▀░░█████████░░▄▀░░░░░░▄▀░░██░░▄▀░░███░░▄▀░░███░░▄▀░░█████████░░▄▀░░░░░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░█")
print("█░░▄▀░░░░░░░░░░█░░▄▀░░██░░▄▀░░██░░▄▀░░███░░▄▀░░███░░▄▀░░█████████░░▄▀░░██░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░█")
print("█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░▄▀░░██░░▄▀░░███░░▄▀░░███░░▄▀░░██░░░░░░█░░▄▀░░██░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█")
print("█░░▄▀░░░░░░░░░░█░░▄▀░░██░░▄▀░░██░░▄▀░░███░░▄▀░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░░░░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░█")
print("█░░▄▀░░█████████░░▄▀░░██░░▄▀░░░░░░▄▀░░███░░▄▀░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██████████░░▄▀░░█░░▄▀░░██░░▄▀░░█")
print("█░░▄▀░░░░░░░░░░█░░▄▀░░██░░▄▀▄▀▄▀▄▀▄▀░░█░░░░▄▀░░░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░██████████░░▄▀░░█░░▄▀░░██░░▄▀░░█")
print("█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░░░░░░░░░▄▀░░█░░▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██████████░░▄▀░░█░░▄▀░░██░░▄▀░░█")
print("█░░░░░░░░░░░░░░█░░░░░░██████████░░░░░░█░░░░░░░░░░█░░░░░░░░░░░░░░█░░░░░░██████████░░░░░░█░░░░░░██░░░░░░█")
print("███████████████████████████████████████████████████████████████████████████████████████████████████████")
print("\n")
print("Made in India. Conquered by Great Britain. Eventually stolen by the United States.")
print("\n")
print("© Copyright Lakshya Chauhan, Rashtriya Swayamsevak Sangh, Democratic National Convention. All rights reserved.")
print("\n")

great = ''
b = 0

while (True):
    great = input("Enter 's' to start and 'q' to quit: ")
    
    if great == 's' or great == 'q':
        break

print("\n")

if great == 's':
    print("Encrypt message: 'e'")
    print("Decrypt message: 'd'")
    print("Quit program: 'b'")
    mainfinal = ''

    while mainfinal != "b":
        print("\n")
        mainfinal = input("Command: ")
        print("\n")

        if(mainfinal == "e"):
            totalstr = ""
            plug1 = []
            plug2 = []
            rotor1a = []
            rotor1b = []
            rotor2a = []
            rotor2b = []
            rotor3a = []
            rotor3b = []

            letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

            for i in range(26):
                character = random.choice(letters)
                totalstr += character
                letters.remove(character)
                plug1.append(character)

            letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

            for i in range(26):
                character = random.choice(letters)
                totalstr += character
                letters.remove(character)
                plug2.append(character)

            letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

            character = random.choice(letters)
            rotor1a.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor1a.append(letters[b])
                else:
                    rotor1a.append(letters[b])
                b += 1

            character = random.choice(letters)
            rotor1b.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor1b.append(letters[b])
                else:
                    rotor1b.append(letters[b])
                b += 1

            character = random.choice(letters)
            rotor2a.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor2a.append(letters[b])
                else:
                    rotor2a.append(letters[b])
                b += 1

            character = random.choice(letters)
            rotor2b.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor2b.append(letters[b])
                else:
                    rotor2b.append(letters[b])
                b += 1

            character = random.choice(letters)
            rotor3a.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor3a.append(letters[b])
                else:
                    rotor3a.append(letters[b])
                b += 1

            character = random.choice(letters)
            rotor3b.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor3b.append(letters[b])
                else:
                    rotor3b.append(letters[b])
                b += 1

            request = (input("Enter message: ")).upper()
            print("\n")

            rotor1 = 0
            rotor2 = 0
            rotor3 = 0

            totalstr += (rotor1a[0] + rotor1b[0] + rotor2a[0] + rotor2b[0] + rotor3a[0] + rotor3b[0])
            totalstr += " "

            for r in range(len(request)):
                if request[r] in letters:
                    question = request[r]
                    question = plug2[key(question, plug1)]
                    
                    question = rotor1b[key(question, rotor1a)]
                    question = rotor2b[key(question, rotor2a)]
                    question = rotor3b[key(question, rotor3a)]

                    if key(question, rotor3b) == 25:
                        question = rotor3b[0]
                    else:
                        question = rotor3b[key(question, rotor3b) + 1]
                    
                    question = rotor3a[key(question, rotor3b)]
                    question = rotor2a[key(question, rotor2b)]
                    question = rotor1a[key(question, rotor1b)]

                    question = plug1[key(question, plug2)]
                    totalstr += question

                    if rotor1 == 25:
                        rotor1 = -1
                        if rotor2a == 25:
                            rotor2 = -1
                            if rotor3a == 25:
                                rotor3 = -1
                            rotor3a = turn(rotor3a)
                            rotor3 += 1
                        rotor2a = turn(rotor2a)
                        rotor2 += 1
                    rotor1a = turn(rotor1a)
                    rotor1 += 1
                else:
                    totalstr += request[r]
            
            print("Encrypted message: " + totalstr)
        elif(mainfinal == "d"):
            request = (input("Enter message: ")).upper()
            print("\n")

            totalstr = ""
            plug1 = []
            plug2 = []
            rotor1a = []
            rotor1b = []
            rotor2a = []
            rotor2b = []
            rotor3a = []
            rotor3b = []

            for i in range(26):
                plug1.append(request[0])
                request = request[1:]
            
            for i in range(26):
                plug2.append(request[0])
                request = request[1:]
            
            letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

            character = request[0]
            request = request[1:]
            rotor1a.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor1a.append(letters[b])
                else:
                    rotor1a.append(letters[b])
                b += 1

            character = request[0]
            request = request[1:]
            rotor1b.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor1b.append(letters[b])
                else:
                    rotor1b.append(letters[b])
                b += 1

            character = request[0]
            request = request[1:]
            rotor2a.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor2a.append(letters[b])
                else:
                    rotor2a.append(letters[b])
                b += 1

            character = request[0]
            request = request[1:]
            rotor2b.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor2b.append(letters[b])
                else:
                    rotor2b.append(letters[b])
                b += 1

            character = request[0]
            request = request[1:]
            rotor3a.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor3a.append(letters[b])
                else:
                    rotor3a.append(letters[b])
                b += 1

            character = request[0]
            request = request[1:]
            rotor3b.append(character)

            b = key(character, letters)
            b += 1
            for i in range (25):
                if b > 25:
                    b = 0
                    rotor3b.append(letters[b])
                else:
                    rotor3b.append(letters[b])
                b += 1

            rotor1 = 0
            rotor2 = 0
            rotor3 = 0
            
            request[1:]

            for r in range(len(request)):
                if request[r] in letters:
                    question = request[r]
                    question = plug2[key(question, plug1)]
                    
                    question = rotor1b[key(question, rotor1a)]
                    question = rotor2b[key(question, rotor2a)]
                    question = rotor3b[key(question, rotor3a)]

                    if key(question, rotor3b) == 0:
                        question = rotor3b[25]
                    else:
                        question = rotor3b[key(question, rotor3b) - 1]
                    
                    question = rotor3a[key(question, rotor3b)]
                    question = rotor2a[key(question, rotor2b)]
                    question = rotor1a[key(question, rotor1b)]

                    question = plug1[key(question, plug2)]
                    totalstr += question

                    if rotor1 == 25:
                        rotor1 = -1
                        if rotor2a == 25:
                            rotor2 = -1
                            if rotor3a == 25:
                                rotor3 = -1
                            rotor3a = negturn(rotor3a)
                            rotor3 += 1
                        rotor2a = negturn(rotor2a)
                        rotor2 += 1
                    rotor1a = negturn(rotor1a)
                    rotor1 += 1
                else:
                    totalstr += request[r]
            
            print("Decrypted message:" + totalstr)