import random

questions = {
    "What is the capital of Japan?": "Tokyo",
    "Who developed the theory of relativity?": "Albert Einstein",
    "What is the largest ocean on Earth?": "Pacific Ocean",
    "How many continents are there?": "Seven",
    "What is the chemical symbol for water?": "H2O",
    "Which planet is known as the Red Planet?": "Mars",
    "Who painted the Mona Lisa?": "Leonardo da Vinci",
    "What is the square root of 81?": "9",
    "who are you?": "yadhu",
    "How many legs does a spider have?": "Eight",
    "Which is the longest river in the world?": "Nile River"
}
def python_trivia_game():
    questions_list = list(questions.keys())
    total_questions = 5
    score = 0
selected_questions = random.sample(questions_list, total_questions)
python_trivia_game()