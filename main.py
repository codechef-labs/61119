import random
import time
import json
import os
from typing import List, Dict, Tuple

class Word:
    def __init__(self, word: str, hint: str, direction: str, x: int, y: int):
        self.word = word.upper()
        self.hint = hint
        self.direction = direction  # 'across' or 'down'
        self.x = x  # starting x coordinate
        self.y = y  # starting y coordinate
        self.is_solved = False

class Board:
    def __init__(self, size: int = 15):
        self.size = size
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.words: List[Word] = []
        self.solution_grid = None

    def can_place_word(self, word: str, x: int, y: int, direction: str) -> bool:
        if direction == 'across':
            if y + len(word) > self.size:
                return False
            for i in range(len(word)):
                if self.grid[x][y+i] != ' ' and self.grid[x][y+i] != word[i]:
                    return False
        else:  # down
            if x + len(word) > self.size:
                return False
            for i in range(len(word)):
                if self.grid[x+i][y] != ' ' and self.grid[x+i][y] != word[i]:
                    return False
        return True

    def place_word(self, word: Word):
        for i in range(len(word.word)):
            if word.direction == 'across':
                self.grid[word.x][word.y + i] = word.word[i]
            else:
                self.grid[word.x + i][word.y] = word.word[i]
        self.words.append(word)

    def find_intersection(self, word: str, placed_word: Word) -> List[Tuple[int, int, str]]:
        intersections = []
        for i, letter in enumerate(word):
            if word[i] in placed_word.word:
                for j, placed_letter in enumerate(placed_word.word):
                    if letter == placed_letter:
                        if placed_word.direction == 'across':
                            x = placed_word.x
                            y = placed_word.y + j
                            intersections.append((x, y, 'down'))
                        else:
                            x = placed_word.x + j
                            y = placed_word.y
                            intersections.append((x, y, 'across'))
        return intersections

    def create_crossword(self, words_and_hints: Dict[str, str]):
        if not words_and_hints:
            return False

        # Sort words by length (longest first)
        sorted_words = sorted(words_and_hints.keys(), key=len, reverse=True)

        # Place first word in the middle horizontally
        first_word = sorted_words[0]
        x = self.size // 2
        y = (self.size - len(first_word)) // 2
        self.place_word(Word(first_word, words_and_hints[first_word], 'across', x, y))

        # Try to place remaining words
        for word in sorted_words[1:]:
            placed = False
            for placed_word in self.words:
                intersections = self.find_intersection(word, placed_word)
                random.shuffle(intersections)
                
                for x, y, direction in intersections:
                    if direction == 'across':
                        start_y = y - word.index(placed_word.word[x - placed_word.x])
                        if self.can_place_word(word, x, start_y, direction):
                            self.place_word(Word(word, words_and_hints[word], direction, x, start_y))
                            placed = True
                            break
                    else:  # down
                        start_x = x - word.index(placed_word.word[y - placed_word.y])
                        if self.can_place_word(word, start_x, y, direction):
                            self.place_word(Word(word, words_and_hints[word], direction, start_x, y))
                            placed = True
                            break
                if placed:
                    break

        # Store solution grid
        self.solution_grid = [row[:] for row in self.grid]
        # Clear grid for gameplay
        for word in self.words:
            for i in range(len(word.word)):
                if word.direction == 'across':
                    self.grid[word.x][word.y + i] = '_'
                else:
                    self.grid[word.x + i][word.y] = '_'

        return True

    def display(self):
        print("\n   " + " ".join([f"{i:2}" for i in range(self.size)]))
        for i in range(self.size):
            print(f"{i:2} |" + "|".join(f"{cell:2}" for cell in self.grid[i]) + "|")

    def get_word_numbers(self):
        numbered_positions = {}
        counter = 1
        for word in self.words:
            pos = (word.x, word.y)
            if pos not in numbered_positions:
                numbered_positions[pos] = counter
                counter += 1
        return numbered_positions

class Game:
    def __init__(self):
        self.board = Board()
        self.player_name = ""
        self.score = 0
        self.start_time = None
        self.words_and_hints = {}

    def create_game(self):
        print("\n=== Create New Crossword ===")
        print("Enter words and hints (enter blank line to finish):")
        while True:
            word = input("Enter word (or press Enter to finish): ").strip().upper()
            if not word:
                break
            hint = input(f"Enter hint for {word}: ").strip()
            self.words_and_hints[word] = hint

        if not self.board.create_crossword(self.words_and_hints):
            print("Failed to create crossword. Please try with different words.")
            return False
        return True

    def play(self):
        self.player_name = input("\nEnter your name: ")
        self.score = 0
        self.start_time = time.time()
        
        numbered_positions = self.board.get_word_numbers()
        words_by_number = {}
        for word in self.board.words:
            number = numbered_positions.get((word.x, word.y))
            if number:
                words_by_number[number] = word

        while not all(word.is_solved for word in self.board.words):
            self.board.display()
            print("\nClues:")
            for number, word in words_by_number.items():
                direction = "across" if word.direction == 'across' else "down  "
                solved = "(SOLVED)" if word.is_solved else ""
                print(f"{number:2}. {direction} - {word.hint} {solved}")

            try:
                number = int(input("\nEnter number (or 0 to quit): "))
                if number == 0:
                    break
                if number not in words_by_number:
                    print("Invalid number!")
                    continue

                word = words_by_number[number]
                if word.is_solved:
                    print("This word is already solved!")
                    continue

                guess = input("Enter your guess: ").strip().upper()
                if guess == word.word:
                    word.is_solved = True
                    self.score += 10
                    # Update grid with correct word
                    for i in range(len(word.word)):
                        if word.direction == 'across':
                            self.board.grid[word.x][word.y + i] = word.word[i]
                        else:
                            self.board.grid[word.x + i][word.y] = word.word[i]
                    print("Correct! +10 points")
                else:
                    print("Incorrect! Try again.")
                    self.score -= 2

            except ValueError:
                print("Please enter a valid number!")

        time_taken = int(time.time() - self.start_time)
        self.save_score(time_taken)
        self.display_final_results(time_taken)

    def save_score(self, time_taken):
        score_data = {
            'player': self.player_name,
            'score': self.score,
            'time': time_taken,
            'words_solved': sum(1 for word in self.board.words if word.is_solved),
            'total_words': len(self.board.words),
            'date': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        scores = []
        if os.path.exists('crossword_scores.json'):
            with open('crossword_scores.json', 'r') as f:
                scores = json.load(f)
        
        scores.append(score_data)
        
        with open('crossword_scores.json', 'w') as f:
            json.dump(scores, f, indent=4)

    def display_final_results(self, time_taken):
        print("\n=== Game Over ===")
        print(f"Player: {self.player_name}")
        print(f"Final Score: {self.score}")
        print(f"Time Taken: {time_taken} seconds")
        print(f"Words Solved: {sum(1 for word in self.board.words if word.is_solved)}/{len(self.board.words)}")
        
        # Show solution
        print("\nFinal Solution:")
        temp_grid = self.board.grid
        self.board.grid = self.board.solution_grid
        self.board.display()
        self.board.grid = temp_grid

def main():
    while True:
        print("\n=== Crossword Puzzle Game ===")
        print("1. Create and Play New Game")
        print("2. View High Scores")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            game = Game()
            if game.create_game():
                game.play()
        elif choice == '2':
            if os.path.exists('crossword_scores.json'):
                with open('crossword_scores.json', 'r') as f:
                    scores = json.load(f)
                print("\n=== High Scores ===")
                for score in sorted(scores, key=lambda x: x['score'], reverse=True)[:5]:
                    print(f"Player: {score['player']}")
                    print(f"Score: {score['score']}")
                    print(f"Words: {score['words_solved']}/{score['total_words']}")
                    print(f"Time: {score['time']} seconds")
                    print(f"Date: {score['date']}")
                    print("-" * 30)
            else:
                print("No scores yet!")
        elif choice == '3':
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
