import telebot
from telebot.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import json
import pyjokes
import random
import emoji
from questions_db import questions_db

bot = telebot.TeleBot('')

ADMIN = []
word_list = ["python", "telegram", "bot", "game", "wonder", "guess", "play", "fun"]
game_data = {}
choices = ["Rock", "Paper", "Scissors"]
target_number = 0
attempts_for_guess = 0 
greeting_shown = {}

DATA_FILE = 'user_data.json'

def load_user_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

user_data = load_user_data()

@bot.message_handler(commands=['start'])
def start(message: Message):
    if message.chat.id not in ADMIN and message.chat.id not in greeting_shown:
        greeting_shown[message.chat.id] = True
        key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = KeyboardButton(text='Interesting games')
        button2 = KeyboardButton(text='Little-bit recommends')
        key_board.add(button1, button2)

        bot.send_photo(
            message.chat.id,
            photo= "https://cdn-icons-png.flaticon.com/512/4712/4712024.png",
            caption= "Hi my dear User 👋!!\nI'm your bot telegram 😄\n (Pick an option on the keyboard)",
            reply_markup=key_board
        )
    else:
        show_main_menu(message)

def show_main_menu(message: Message):
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Interesting games')
    button2 = KeyboardButton(text='Little-bit recommends')
    key_board.add(button1, button2)
    bot.send_message(message.chat.id, "Please choose an option:", reply_markup=key_board)

@bot.message_handler(func=lambda message: message.text == 'Interesting games')
def handle_interesting_games(message: Message):
    games(message)

@bot.message_handler(func=lambda message: message.text == 'Little-bit recommends')
def handle_recommends(message: Message):
    recommends_bot(message)


def games(message: Message):
    bot.send_message(message.chat.id, "You have the following games:\n- Field of wonders✍️\n- Who wants to become a millionaire?\n- Guess a number❓\n- Rock, Paper, Scissors✂️📄")
    
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Field of wonders')
    button2 = KeyboardButton(text='Who wants to become a millionaire?')
    button3 = KeyboardButton(text='Guess a number')
    button4 = KeyboardButton(text='Rock, Paper, Scissors')
    button5 = KeyboardButton(text='Back to menu')

    key_board.add(button1, button2, button3, button4, button5)

    sent_message = bot.send_message(message.chat.id, "Select the game you want:", reply_markup=key_board)
    bot.register_next_step_handler(sent_message, handle_message_of_games)


def handle_message_of_games(message: Message):
    if message.text == "Field of wonders":
        start_field_of_wonders_game(message)
    elif message.text == "Who wants to become a millionaire?":
        start_of_mill(message)
    elif message.text == "Guess a number":
        start_guess_number_game(message)
    elif message.text == "Rock, Paper, Scissors":
        start_game_of_rps(message)
    elif message.text == "Back to menu":
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, "Invalid selection, please choose a game or 'Back to menu'.")
        games(message)


def start_of_mill(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Play'), KeyboardButton('Back to menu'))
    bot.send_message(message.chat.id, "Це гра 'Хто хоче стати мільйонером?'.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Play')
def play(message: Message):
    user_data[message.chat.id] = {
        'score': 50, 
        'asked_questions': []
    }
    save_user_data(user_data)
    ask_random_question(message)  


@bot.message_handler(func=lambda message: message.text == 'Back to menu')
def back_to_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Play'), KeyboardButton('Back to menu'))
    bot.send_message(message.chat.id, "Ви повернулись до головного меню.", reply_markup=markup)
    games(message)


def ask_random_question(message: Message):  
    chat_id = message.chat.id
    user_info = user_data.get(chat_id)
    asked_questions = user_info['asked_questions']
    remaining_questions = [qid for qid in questions_db.keys() if qid not in asked_questions]
    
    if not remaining_questions:
        bot.send_message(chat_id, f"Ви закінчили гру! Ваш рахунок: {user_info['score']}")
        del user_data[chat_id]
        save_user_data(user_data)
        return

    question_id = random.choice(remaining_questions)
    user_info['asked_questions'].append(question_id)
    question_data = questions_db[question_id]
    question = question_data["question"]
    options = question_data["options"]
    image_url = question_data["URL-question"]  

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in options:
        markup.add(KeyboardButton(option))
    markup.add(KeyboardButton("Back to menu"))

    bot.send_photo(chat_id, photo=image_url, caption=f"Запитання: {question}", reply_markup=markup)
    save_user_data(user_data)


def check_answer(message: Message, user_answer): 
    chat_id = message.chat.id
    user_info = user_data.get(chat_id)
    last_question_id = user_info['asked_questions'][-1]
    correct_answer = questions_db[last_question_id]['correct']

    if user_answer.upper().startswith(correct_answer):
        user_info['score'] *= 2
        bot.send_message(chat_id, f"Правильно! Ваш поточний рахунок: {user_info['score']}. Наступне запитання...")
        ask_random_question(message)  
    else:
        bot.send_message(chat_id, f"Неправильно! Правильна відповідь: {correct_answer}. Гра закінчена.\nВаш остаточний рахунок: {user_info['score']}.")
        del user_data[chat_id]
        save_user_data(user_data)
        back_to_menu(message)  


@bot.message_handler(func=lambda message: message.text.startswith(('A', 'B', 'C', 'D')))
def answer(message: Message):
    chat_id = message.chat.id
    user_info = user_data.get(chat_id)

    if user_info:
        user_answer = message.text.strip().upper()
        check_answer(message, user_answer)  



def start_guess_number_game(message: Message):
    target_number = random.randint(1, 100)
    attempts_for_guess = 0
    bot.send_message(message.chat.id, "I've picked a number between 1 and 100. Try to guess it!")
    bot.send_message(message.chat.id, "Send your guess (a number between 1 and 100):")
    bot.register_next_step_handler(message, lambda msg: guess_number(msg, target_number, attempts_for_guess))

def guess_number(message: Message, target_number: int, attempts_for_guess: int):
    try:
        guess = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number between 1 and 100.")
        return bot.register_next_step_handler(message, lambda msg: guess_number(msg, target_number, attempts_for_guess))

    attempts_for_guess += 1

    if guess < target_number:
        bot.send_message(message.chat.id, "Too low! Try again.")
        bot.register_next_step_handler(message, lambda msg: guess_number(msg, target_number, attempts_for_guess))
    elif guess > target_number:
        bot.send_message(message.chat.id, "Too high! Try again.")
        bot.register_next_step_handler(message, lambda msg: guess_number(msg, target_number, attempts_for_guess))
    else:
        bot.send_message(message.chat.id, f"Congratulations! You guessed the number in {attempts_for_guess} attempts!")
        handle_interesting_games(message)

def start_game_of_rps(message: Message):
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text="Rock")
    button2 = KeyboardButton(text="Paper")
    button3 = KeyboardButton(text="Scissors")
    key_board.add(button1, button2, button3)

    sent_message = bot.send_photo(message.chat.id,photo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQK2hjx56TFg7oUrkPoStVlJEM-Az560Pa2lQ&s", 
                    caption= "Choose your option:", reply_markup=key_board)
    bot.register_next_step_handler(sent_message, play_rps)

def play_rps(message: Message):
    user_choice = message.text
    if user_choice not in choices:
        bot.send_message(message.chat.id, "Invalid choice. Please choose Rock, Paper, or Scissors.")
        return start_game_of_rps(message)

    bot_choice = random.choice(choices)
    bot.send_message(message.chat.id, f"Bot chose: {bot_choice}")

    if user_choice == bot_choice:
        result = "It's a draw!"
    elif (user_choice == "Rock" and bot_choice == "Scissors") or \
         (user_choice == "Paper" and bot_choice == "Rock") or \
         (user_choice == "Scissors" and bot_choice == "Paper"):
        result = "Congratulations, you win!"
    else:
        result = "Sorry, you lose."

    bot.send_message(message.chat.id, result)

    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text="Play again")
    button2 = KeyboardButton(text="Exit")
    key_board.add(button1, button2)

    sent_message = bot.send_message(message.chat.id, "Would you like to play again?", reply_markup=key_board)
    bot.register_next_step_handler(sent_message, handle_play_again_of_rpz)

def handle_play_again_of_rpz(message: Message):
    if message.text == "Play again":
        start_game_of_rps(message)
    elif message.text == "Exit":
        bot.send_message(message.chat.id, "Thanks for playing! See you next time.")
        games(message)
    else:
        bot.send_message(message.chat.id, "Invalid option. Please choose 'Play again' or 'Exit'.")
        bot.register_next_step_handler(message, handle_play_again_of_rpz)

def start_field_of_wonders_game(message: Message):
    word_to_guess = random.choice(word_list)
    game_data[message.chat.id] = {
        'word_to_guess': word_to_guess,
        'guessed_letters': set(),
        'attempts': 6
    }
    bot.send_message(message.chat.id, "Let's play 'Field of wonders'! You have 6 attempts to guess the word.")
    show_current_word_state(message)

def show_current_word_state(message: Message):
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Back to menu')
    key_board.add(button1)
    game_state = game_data[message.chat.id]
    word_to_guess = game_state['word_to_guess']
    guessed_letters = game_state['guessed_letters']
    attempts = game_state['attempts']

    if message.text == 'Back to menu':
        games(message)
    else:    
        displayed_word = ' '.join([letter if letter in guessed_letters else '_' for letter in word_to_guess])
        bot.send_message(message.chat.id, f"Word: {displayed_word}\nAttempts left: {attempts}\nGuess a letter:")
        bot.register_next_step_handler(message, process_guess)

def process_guess(message: Message):
    game_state = game_data.get(message.chat.id)
    if not game_state:
        bot.send_message(message.chat.id, "No game in progress. Type 'Play Поле чудес' to start a new game.")
        return

    letter = message.text.lower()
    if len(letter) != 1 or not letter.isalpha():
        if message.text == 'Back to menu':
            return games(message)
        bot.send_message(message.chat.id, "Please guess a single letter.")
        return show_current_word_state(message)

    guessed_letters = game_state['guessed_letters']
    if letter in guessed_letters:
        bot.send_message(message.chat.id, "You've already guessed that letter.")
        return show_current_word_state(message)

    guessed_letters.add(letter)

    if letter in game_state['word_to_guess']:
        bot.send_message(message.chat.id, "Good guess!")
    else:
        game_state['attempts'] -= 1
        bot.send_message(message.chat.id, "Wrong guess!")

    if game_state['attempts'] == 0:
        bot.send_message(message.chat.id, f"You lost! The word was: {game_state['word_to_guess']}.")
        del game_data[message.chat.id]
        games(message)
    elif all(letter in guessed_letters for letter in game_state['word_to_guess']):
        bot.send_message(message.chat.id, "Congratulations! You've guessed the word!")
        del game_data[message.chat.id]
        games(message)
    else:
        show_current_word_state(message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    bot.send_message(message.chat.id, "Sorry, I didn't understand that. Please choose an option from the menu.")


def recommends_bot(message: Message):    
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Amazing films')
    button2 = KeyboardButton(text='Cool music')
    button3 = KeyboardButton(text='Games by genre')
    button4 = KeyboardButton(text='Funny anecdots')
    button5 = KeyboardButton(text='Interestig history')
    button6 = KeyboardButton(text='Back to menu')
    key_board.add(button1, button2, button3, button4, button5, button6)

    sent_message = bot.send_message(message.chat.id, "BOT recommends for you: "\
        "\n- Films📽️🎬 \n- Music🎼🎺 \n- Games by genre🎰🎮 \n- Anecdots😂😂 \n- Interestig history🤫🤫"\
        "\n Select recommends from BOT, what are you want:", reply_markup = key_board)
    
    bot.register_next_step_handler(sent_message, handle_message)

             

def handle_message(message: Message):
    if message.text == "Amazing films":
        films(message)
    elif message.text == "Cool music":
        musics(message)
    elif message.text == "Games by genre":
        games_by_genre(message)
    elif message.text == "Funny anecdots":
        jokes(message)
    elif message.text == "Interestig history":
        interesting_history(message)
    elif message.text == "Back to menu":
        start(message)
    else:
        print("Wrong select operations")


def jokes(message: Message):
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Generations joke')
    button2 = KeyboardButton(text='Back to menu')
    key_board.add(button1, button2)
    
    sent_message = bot.send_message(message.chat.id, f"Select your opperation: ", reply_markup=key_board)
    bot.register_next_step_handler(sent_message, generation_joke)


def generation_joke(message:Message):
    if message.text == "Generations joke":
        joke = pyjokes.get_joke()
        bot.send_message(message.chat.id, f"BOT: \n{joke}")
        jokes(message)
    elif message.text == "Back to menu":
        recommends_bot(message)


def games_by_genre(message: Message):
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Action')
    button2 = KeyboardButton(text='Adventure')
    button3 = KeyboardButton(text='Puzzle')
    button4 = KeyboardButton(text='Strategy')
    button5 = KeyboardButton(text='Back to menu')
    key_board.add(button1, button2, button3, button4, button5)

    sent_message = bot.send_message(message.chat.id, "Select your favorite genre of games: ", reply_markup=key_board)
    bot.register_next_step_handler(sent_message, games_of_genre)


def games_of_genre(message: Message):
    if message.text == "Action":
        list_of_action_games = ["Call of Duty", "Doom", "Halo", "GTA V", "Red Dead Redemption 2"]
        bot.send_message(message.chat.id, f"Action game: '{random.choice(list_of_action_games)}'")
        games_by_genre(message)
    elif message.text == "Adventure":
        list_of_adventure_games = ["The Legend of Zelda", "Uncharted", "Tomb Raider", "Firewatch", "Graveyard Keeper"]
        bot.send_message(message.chat.id, f"Adventure game: '{random.choice(list_of_adventure_games)}'")
        games_by_genre(message)
    elif message.text == "Puzzle":
        list_of_puzzle_games = ["Portal", "The Witness", "Tetris", "Limbo", "Candy Crush"]
        bot.send_message(message.chat.id, f"Puzzle game: '{random.choice(list_of_puzzle_games)}'")
        games_by_genre(message)
    elif message.text == "Strategy":
        list_of_strategy_games = ["StarCraft", "Civilization", "Age of Empires", "XCOM", "Total War"]
        bot.send_message(message.chat.id, f"Strategy game: '{random.choice(list_of_strategy_games)}'")
        games_by_genre(message)
    elif message.text == "Back to menu":
        recommends_bot(message)


def musics(message:Message):
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Pop-music')
    button2 = KeyboardButton(text='Rock')
    button3 = KeyboardButton(text='Phonk')
    button4 = KeyboardButton(text='Classic')
    button5 = KeyboardButton(text='Back to menu')
    key_board.add(button1, button2, button3, button4, button5)

    sent_message = bot.send_message(message.chat.id, "Select your favorite genre musics: ", reply_markup=key_board)
    bot.register_next_step_handler(sent_message, music_of_genre)   


def music_of_genre(message:Message):
    if message.text == "Pop-music":
        list_of_pop_musics = ['Olivia Rodrigo - "Vampire" (2023)', 'Dua Lipa – "Dance the Night" (2023)', 'SZA – "Kill Bill" (2022)', 
    'Miley Cyrus – "Flowers" (2023)', 'Taylor Swift – "Anti-Hero" (2022)', 'The Weeknd, Madonna, Playboi Carti – "Popular" (2023)',
    'Billie Eilish – "What Was I Made For?" (2023)', 'Sam Smith, Kim Petras – "Unholy" (2022)', 'Harry Styles – "As It Was" (2022)',
    'Harry Styles – "As It Was" (2022)', 'Selena Gomez – "Single Soon" (2023)']
        bot.send_message(message.chat.id, f"Pop-music: '{random.choice(list_of_pop_musics)}'")
        musics(message)
    elif message.text == "Rock":
        list_of_rock_musics = ['Foo Fighters – "Run" (2017)', 'Twenty One Pilots – "Heathens" (2016)', 'Royal Blood – "Figure It Out" (2015)',
     'Bring Me The Horizon – "Mantra" (2018)', 'Red Hot Chili Peppers – "Dark Necessities" (2016)', 'Greta Van Fleet – "Highway Tune" (2017)',
     'Arctic Monkeys – "Do I Wanna Know?" (2013)', 'Muse – "Pressure" (2018)', 'The Killers – "Caution" (2020)', 'Imagine Dragons – "Believer" (2017)', 
     'Paramore – "Hard Times" (2017)', 'Maneskin – "I Wanna Be Your Slave" (2021)', 'Ghost – "Square Hammer" (2016)']
        bot.send_message(message.chat.id, f"Rock music: '{random.choice(list_of_rock_musics)}'")
        musics(message)
    elif message.text == "Phonk":
        list_of_phonk_musics = ['Kordhell – "Murder in My Mind" (2021)', 'Pharmacist – "North Memphis" (2022)', 'DJ Smokey – "Creepin n Lurkin" (2015)',
        'Sxmpra – "COWBELL WARRIOR!" (2021)', 'LXST CXNTURY – "INCOMING" (2022)', 'DVRST – "Close Eyes" (2021)', 'Ghostface Playa – "Why Not" (2019)',
        'Interworld – "METAMORPHOSIS" (2022)', 'Sadfriendd – "I Can’t Sleep"', 'PlayaPhonk – "Phonky Town" (2018)', 'DJ Yung Vamp – "I Got Hoes" (2018)',
        'HAARPER – "The Hills" (2019)', 'NxxxxxS – "Platinum Chanel" (2016)', 'Trappin in Japan – "Tokyo Drift" (2020)', 'Freddie Dredd – "GTG" (2019)']      
        bot.send_message(message.chat.id, f"Phonk music: '{random.choice(list_of_phonk_musics)}'")
        musics(message)
    elif message.text == "Classic":
        list_of_classic_musics = ['Max Richter – "Sleep" (2015)', 'Ludovico Einaudi – "Seven Days Walking" (2019)', 'Ólafur Arnalds – "re" (2018)',
        'Hildur Guðnadóttir – "Chernobyl" (2019)', 'Jóhann Jóhannsson – "Orphée" (2016)', "Dustin O'Halloran & Hauschka – 'Lion' (2016)",
        'Max Richter – "Voices" (2020)', 'Philip Glass – "String Quartet No. 8" (2018)', 'Anna Meredith – "FIBS" (2019)', 'Hania Rani – "Esja" (2019)',
        'Nils Frahm – "All Melody" (2018)', 'Víkingur Ólafsson – "Johann Sebastian Bach" (2018)', 'Caroline Shaw – "Orange" (2019)', 'Daniel Pioro – "Dust" (2022)']
        bot.send_message(message.chat.id, f"Classic music: '{random.choice(list_of_classic_musics)}'")
        musics(message)
    elif message.text == "Back to menu":
        recommends_bot(message)


def films(message:Message):
    key_board = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton(text='Fantastic')
    button2 = KeyboardButton(text='Detective')
    button3 = KeyboardButton(text='Comedy')
    button4 = KeyboardButton(text='Horror')
    button5 = KeyboardButton(text='Back to menu')
    key_board.add(button1, button2, button3, button4, button5)

    sent_message = bot.send_message(message.chat.id, "Select your favorite genre films: ", reply_markup=key_board)
    bot.register_next_step_handler(sent_message, films_of_genre)


def films_of_genre(message: Message):
    if message.text == "Fantastic":
        list_of_films_fantastic = ["Blade Runner", "The Matrix", "Inception", "Interstellar", "The Terminator", "Arrival",
                            "2001: A Space Odyssey", "Ex Machina", "Gravity", "Eternal Sunshine of the Spotless Mind"]
        bot.send_message(message.chat.id, f"Film '{random.choice(list_of_films_fantastic)}' of genre 'Fantastic'")
        films(message)
    elif message.text == "Detective":
        list_of_films_detective = ["Se7en", "The Silence of the Lambs", "Zodiac", "Memento", "Gone Girl", "Chinatown", "Shutter Island,"
        "The Girl with the Dragon Tattoo", "Knives Out", "The Usual Suspects"]
        bot.send_message(message.chat.id, f"Film '{random.choice(list_of_films_detective)}' of genre 'Detective'")
        films(message)
    elif message.text == "Comedy":
        list_of_films_comedy = ["Free Guy", "Palm Springs", "The French Dispatch", "Don't Look Up", "Good Boys", "Jojo Rabbit",
        "The Nice Guys", "Game Night", "The Lost City", "Ticket to Paradise"]
        bot.send_message(message.chat.id, f"Film '{random.choice(list_of_films_comedy)}' of genre 'Comedy' ")
        films(message)
    elif message.text == "Horror":
        list_of_films_horror = ["Hereditary", "A Quiet Place", "Get Out", "The Invisible Man", "Midsommar", "It",
        "The Witch", "Us", "The Lighthouse", "Barbarian"]
        bot.send_message(message.chat.id, f"Film '{random.choice(list_of_films_horror)}' of genre 'Horror'")
        films(message)
    elif message.text == "Back to menu":
        recommends_bot(message)


def interesting_history(message: Message):
    history_facts = [
    "In 1969, the first humans landed on the Moon with Apollo 11.",
    "The Great Wall of China is over 13,000 miles long.",
    "In ancient Egypt, servants were sometimes coated in honey to attract flies away from the pharaoh.",
    "Napoleon was once attacked by a horde of rabbits.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
    "During World War II, a Great Dane named Juliana was awarded the Blue Cross Medal for extinguishing an incendiary bomb by urinating on it.",
    "In 1920, Babe Ruth out-homered every American League team except the Yankees.",
    "The longest reigning monarch in history was King Louis XIV of France, who ruled for 72 years.",
    "Cleopatra, the last pharaoh of Egypt, lived closer in time to the Moon landing than to the construction of the Great Pyramid of Giza.",
    "Albert Einstein was offered the presidency of Israel in 1952 but declined.",
    "In 1815, the eruption of Mount Tambora caused the 'Year Without a Summer,' leading to global crop failures.",
    "The original Olympic Games in ancient Greece did not include team sports; all events were individual.",
    "Julius Caesar was kidnapped by pirates and demanded they increase his ransom, as he felt he was worth more.",
    "In 1905, Albert Einstein published his theory of special relativity, forever changing our understanding of physics.",
    "The Roman Empire’s first emperor, Augustus, was the adopted son of Julius Caesar.",
    "During the Great Depression, Al Capone ran a soup kitchen for the unemployed in Chicago.",
    "The Leaning Tower of Pisa began tilting during its construction due to soft ground and a shallow foundation.",
    "The Colosseum in Rome was originally called the Flavian Amphitheatre, named after the Flavian dynasty.",
    "Pablo Picasso could draw before he could walk; his first word was 'pencil'.",
    "The term 'viking' originally meant 'pirate raid' in Old Norse.",
    "Leonardo da Vinci could write with one hand while drawing with the other.",
    "Before alarm clocks were invented, people known as 'knocker-uppers' were hired to wake up workers by tapping on their windows with a stick.",
    "During the Middle Ages, people believed that wearing the herb rosemary could improve memory.",
    "In 1916, a German U-boat sank a British passenger ship called the Lusitania, which helped lead to the U.S. joining WWI.",
    "The word 'robot' comes from the Czech word 'robota,' which means 'forced labor.'",
    "Anne Frank’s diary was published in 1947 by her father, the only member of her family to survive the Holocaust.",
    "During WWII, British intelligence used Monopoly games to smuggle maps, compasses, and money to Allied POWs.",
    "In 1977, Star Wars was released and went on to become one of the highest-grossing films of all time."
]
    random_fact = random.choice(history_facts)
    bot.send_message(message.chat.id, f"Did you know?\n\n{random_fact}")
    recommends_bot(message)


bot.polling(none_stop=True)