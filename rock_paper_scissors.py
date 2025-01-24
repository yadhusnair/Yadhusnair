import random
user_wins = 0
computer_wins = 0
options = ["rock", "paper", "scissors"]
while True:
    user_input = input("Type Rock/Paper/scissors or Q to quit: ").lower()
    if user_input == "q":
        break
    if user_input not in options:
        print("Invalid input. Please choose Rock, Paper, or Scissors.")
        continue
    random_number = random.randint(0,2)
    computer_pick = options[random_number]
    print("computer picked", computer_pick + ".")
    if user_input == computer_pick:
        print("its a tie!, please try again")
    elif (user_input == "rock" and computer_pick == "scissors") or \
         (user_input == "paper" and computer_pick == "rock") or \
         (user_input == "scissors" and computer_pick == "paper"):
        print("you won!")
        user_wins += 1
    else:
        print("you lost!")
        computer_wins += 1
        print("you won", user_wins, "times.")
        print("The computer won", computer_wins, "times.")
        print("goodbye!")
         