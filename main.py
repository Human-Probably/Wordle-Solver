import csv
import os
import sys
import time
from colorama import init, Fore, Back, Style
from collections import Counter
from random import choice as r
import builtins

init()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def best_guess(letters, words, green_letters):
    greens = green_letters.copy()
    possible, x = get_words()
    # breakpoint()
    guesses = []
    for word in possible:
        adding = True
        for letter in word:
            if letter in letters or word.count(letter) > 1:
                adding = False
                break
        if adding:
            guesses.append(word)

    while True:
        try:
            greens.remove("_")
        except ValueError:
            break

    if len(guesses) < 5 or len(greens) >= 3:
        guesses = possible
        searching_letters = set()
        for word in words:
            word = list(word)
            for i in range(5):
                if word[i] not in greens:
                    searching_letters.add(word[i])
        temp = searching_letters.copy()
        for letter in temp:
            counter = 0
            for word in words:
                if letter in word:
                    counter += 1
            if counter == len(words):
                searching_letters.remove(letter)
        letter_counts = Counter(searching_letters)
        guesses = [w for w in guesses if len(set(w)) == len(w)]
        print(f"\n{Style.BRIGHT}Best guesses for missing letters: {Style.RESET_ALL}")
    else:
        print(f"\n{Style.BRIGHT}Best guesses for maximised information: {Style.RESET_ALL}")
        letter_counts = Counter(letter for word in words for letter in word)

    # sort words by total letter commonness (higher = better)
    guesses = sorted(
        guesses,
        key=lambda w: sum(letter_counts[ch] for ch in w),
        reverse=True
    )

    return guesses


def list_all(l, p):
    print("")
    total = 0
    for word in p.keys():
        if word in l:
            total += p[word]
    shortcut = list()
    for i in l[::-1]:
        pos = l.index(i)
        shortcut.append(i)
        print(f"{pos+1}: {Fore.CYAN}{i.upper()}{Style.RESET_ALL} - {(p[i]/total)*100:.2f}%")
    print(f"{Style.BRIGHT}Total number is {len(l)}\n{Style.RESET_ALL}")
    return shortcut[::-1]


def list_10(l, p):
    print("")
    total = 0
    for word in p.keys():
        if word in l:
            total += p[word]
    shortcut = list()
    for i in l[:10][::-1]:
        pos = l.index(i)
        shortcut.append(i)
        print(f"{pos+1}: {Fore.CYAN}{i.upper()}{Style.RESET_ALL} - {(p[i] / total) * 100:.2f}%")
    print(f"{Style.BRIGHT}Total number is {len(l)}\n{Style.RESET_ALL}")
    return shortcut[::-1]


def filtered_green(all_words, letter, position):
    new_words = []
    for word in all_words:
        if word[position] == letter:
            new_words.append(word)
    return new_words


def filtered_amber(all_words, letter, position, app_in_guess, app_in_word):
    new_words = []
    for word in all_words:  # SIMPLE PART
        if letter in word and word[position] != letter:
            new_words.append(word)

    if app_in_guess is not None:
        for word in all_words:
            count = word.count(letter)
            if count < app_in_word:
                try:
                    new_words.remove(word)
                except ValueError:
                    pass

    return new_words


def filtered_red(all_words, letter, app_in_guess, app_in_word, position, final):
    new_words = []
    if app_in_guess is None or app_in_word == 0:  # Simple logic - No repeats
        for word in all_words:
            if letter not in word:
                new_words.append(word)

    else:
        for word in all_words:  # Ouch, only for double letters, removes words with too little of the letters appearing
            count = word.count(letter)
            if ((count >= app_in_word) and not final) or (final and count == app_in_word):  # Don't ask, you won't find out
                new_words.append(word)

    final_words = []
    for word in new_words:
        if word[position] != letter:
            final_words.append(word)

    return final_words


def get_words():
    words = []
    probability = {}

    with open(resource_path("words.csv"), newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue

            word = row[0].strip().lower()

            try:
                prob = float(row[1])
            except (IndexError, ValueError):
                continue

            words.append(word)
            probability[word] = prob

    return words, probability


def validate_word(word):
    words, _ = get_words()

    guess = ""
    for i in word:
        guess += i

    if guess in words:
        return True

    if builtins.input(f"{Fore.RED}Invalid word or spelling, press enter to retry: {Style.RESET_ALL}") in ("", " "):
        return False
    return True


def instruct():
    print(f"+ to repeat the controls")
    print("/ to restart the game")
    print("\\ to exit the program")
    print("% to activate speedrun mode")
    print("- to undo last guess")
    print("# to view the history")
    print("@ to repeat top ten words")
    print("! to list all current possible words")
    print(f"? to get exploration words{Style.RESET_ALL}")


def main():

    words, probs = get_words()
    memory = None
    speed_run = False
    speed_run_current = None
    speed_run_used = False
    shortcut = list()
    for i in range(5):
        while True:
            adding = True
            add = r(words)
            for letter in add:
                if add.count(letter) > 1:
                    adding = False
                    break
            if not adding:
                continue
            break
        shortcut.append(add)
    history = []
    output = ""
    green_letters = ["_" for _ in range(5)]

    # words list is all current possible words in order

    print("\033[2J\033[H", end="")
    print(f"{Fore.LIGHTBLACK_EX}GAME HAS BEEN RESET\n{Style.RESET_ALL}")
    instruct()

    known_letters = set()
    while True:

        if speed_run:
            guess = ""
            if speed_run_current is None:
                print(f"{Fore.YELLOW}Speedrun mode ended, Deactivated{Style.RESET_ALL}")
                speed_run = False
                continue

            elif speed_run_current == "stair":
                speed_run_current = "lemon"
                guess = "stair"
            elif speed_run_current == "lemon":
                speed_run_current = "pudgy"
                guess = "lemon"
            elif speed_run_current == "pudgy":
                speed_run_current = None
                guess = "pudgy"

            cancel = False
            while True:
                result = list(builtins.input(f"\n{Fore.LIGHTWHITE_EX}Next guess: {Fore.CYAN}{guess.upper()}"
                                             f"{Fore.LIGHTWHITE_EX}\nResult (RAG): {Style.RESET_ALL}").lower())

                try:
                    if result[0] == "%":
                        cancel = True
                        break
                except IndexError:
                    continue

                allowed = tuple("rag")
                if result == ["r"]:
                    result = ["r" for _ in range(5)]
                if result == ["g"]:
                    result = ["g" for _ in range(5)]
                result = [item for item in result if item in allowed]

                if len(result) != 5:
                    print(f"{Fore.RED}Error, Try again{Style.RESET_ALL}")
                    continue

                output = "\n "
                for i in range(5):
                    addition = ""
                    if result[i] == "r":
                        addition = Back.WHITE + Fore.BLACK
                    elif result[i] == "a":
                        addition = Back.YELLOW + Fore.BLACK
                    elif result[i] == "g":
                        addition = Back.GREEN + Fore.BLACK
                    output = output + addition + " " + guess[i].upper() + " " + Style.RESET_ALL + " "

                if builtins.input(output + Fore.LIGHTWHITE_EX + f"\nIf this is wrong type 'N', otherwise enter anything: {Style.RESET_ALL}") not in ("n", "N"):
                    continue

                break

            if cancel:
                speed_run_current = None
                continue

        else:
            guess = builtins.input(f"\n{Fore.LIGHTWHITE_EX}Next guess: {Style.RESET_ALL}").lower()

            if guess == "!":
                shortcut = list_all(words, probs)
                continue
            elif guess == "?":
                try:
                    best = best_guess(known_letters, words, green_letters)
                    if len(best) == 0:
                        print(f"{Fore.RED}Error, Try again{Style.RESET_ALL}")
                        continue
                    shortcut = list()
                    for i in range(5)[::-1]:
                        shortcut.append(best[i])
                        print(str(i+1) + ": " + Fore.CYAN + best[i].upper() + Style.RESET_ALL)
                except IndexError:
                    pass
                shortcut = shortcut[::-1]
                continue
            elif guess == "/":
                return True
            elif guess == "\\":
                print(f"{Fore.GREEN}Thank you for using.{Style.RESET_ALL}")
                time.sleep(2)
                return False
            elif guess == "-" and memory is not None:
                words, history, known_letters = memory[0], memory[1][:-1], memory[2]
                shortcut = list_10(words, probs)
                continue
            elif guess == "#" and memory is not None:
                print()
                for word in history:
                    print(word)
                print()
                continue
            elif guess == "@":
                shortcut = list_10(words, probs)
                continue
            elif guess == "%":
                if not speed_run_used:
                    speed_run = True
                    speed_run_used = True
                    speed_run_current = "stair"
                    print(f"{Fore.YELLOW}Speedrun Activated, % again to Deactivate{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}Error, Try again{Style.RESET_ALL}")
                continue
            elif guess.isdigit():
                try:
                    guess = [shortcut[int(guess)-1]][0]
                    print(Fore.CYAN + guess.upper() + Style.RESET_ALL)
                except IndexError:
                    pass
            elif guess == "+":
                instruct()
                continue

            guess = list(guess)
            allowed = tuple("abcdefghijklmnopqrstuvwxyz")
            guess = [item for item in guess if item in allowed]

            if len(guess) != 5:
                print(f"{Fore.RED}Error, Try again{Style.RESET_ALL}")
                continue

            if not validate_word(guess):
                continue

            result = list(builtins.input(f"{Fore.LIGHTWHITE_EX}Result (RAG): {Style.RESET_ALL}").lower())
            allowed = tuple("rag")
            if result == ["r"]:
                result = ["r" for _ in range(5)]
            if result == ["g"]:
                result = ["g" for _ in range(5)]
            result = [item for item in result if item in allowed]

            if len(result) != 5:
                print(f"{Fore.RED}Error, Try again{Style.RESET_ALL}")
                continue

            output = "\n "
            for i in range(5):
                addition = ""
                if result[i] == "r":
                    addition = Back.WHITE + Fore.BLACK
                elif result[i] == "a":
                    addition = Back.YELLOW + Fore.BLACK
                elif result[i] == "g":
                    addition = Back.GREEN + Fore.BLACK
                output = output + addition + " " + guess[i].upper() + " " + Style.RESET_ALL + " "

            if builtins.input(output + Style.RESET_ALL + f"\n{Fore.LIGHTWHITE_EX}If this is wrong type 'N', otherwise enter anything: "
                                                         f"{Style.RESET_ALL}") not in ("n", "N"):
                continue

        memory = [words, history, known_letters, ]  # May require more in future

        # Processing of lists guess and result done at this stage
        # Guess list is the users inputted word
        # Results list is the corresponding result from wordle presented by Red, Amber, Green

        # Begin iteration through letters and filtration of the words list

        for pos, letter in enumerate(guess):

            value = result[pos]  # value is the RAG result of the current letter
            indexes = [i for i, x in enumerate(guess) if x == letter]  # Positions of all appearances of the letter in guess
            all_appearances = [result[i] for i in indexes]  # All values (RAG) of the letter throughout

            if len(indexes) > 1:
                repeats = len(indexes)  # Number of times the letter appears in the guess
                confirmed_appearances = sum(x in ("a", "g") for x in all_appearances)  # Confirmed number of times the letter appears in the word
                final_appearances = "r" in all_appearances

            else:  # Allows for workaround if letter appears only once in the guess
                repeats = None
                confirmed_appearances = None
                final_appearances = None

            if value == "g":
                words = filtered_green(words, letter, pos)
                known_letters.add(letter)
                green_letters[pos] = letter
            if value == "a":
                words = filtered_amber(words, letter, pos, repeats, confirmed_appearances)
                known_letters.add(letter)
            if value == "r":
                words = filtered_red(words, letter, repeats, confirmed_appearances, pos, final_appearances)
                known_letters.add(letter)

        shortcut = list_10(words, probs)
        history.append(output)

        if len(words) == 1:
            output = ""
            for i in range(5):
                addition = Back.GREEN + Fore.BLACK
                output = output + addition + " " + words[0][i].upper() + " " + Style.RESET_ALL + " "
            print(output)
            output = "\n " + output
            if output not in history:
                history.append(output)
            if builtins.input(f"\n{Fore.GREEN}Congratulations! Press Enter to start new: {Style.RESET_ALL}") in ("", " "):
                return True


if __name__ == "__main__":
    try:
        while True:
            if not main():
                break
    except KeyboardInterrupt:
        print(f"{Fore.GREEN}\n\nThank you for using.{Style.RESET_ALL}")
        time.sleep(2)
        sys.exit()
    sys.exit()
