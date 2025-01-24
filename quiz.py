print("Welcome to my computer quiz!")   
playing = input("Do you want to play? ")

if playing.lower() != "yes":
    print("Okay, maybe next time!")  # This will execute if the user says no.
    quit()

print("Okay! Let's play!")  # This will only execute if the user says yes.
score = 0
answer = input("What does CPU stand for? ")
if answer.lower() == "central processing unit":
    print("Correct!")
    score += 1
else:
    print("Incorrect!")

answer = input("What does RAM stand for? ")
if answer.lower() == "random access memory":  # Make sure the "r" in "random" is lowercase.
    print("Correct!")
    score += 1
else:
    print("Incorrect!")

answer = input("What does PSU stand for? ")
if answer.lower() == "power supply unit":
    print("Correct!")
    score += 1
else:
    print("Incorrect!")

answer = input("What does SCU stand for? ")
if answer.lower() == "serial communication unit":
    print("Correct!")
    score += 1
else:   
    print("Incorrect!")
print("you got " + str(score) + " questions correct!")
print("you got " + str((score/4)*100) + "% .")
