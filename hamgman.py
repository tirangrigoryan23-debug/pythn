def is_possible_to_create_word(letters, word):
    for c in word:
        if c not in letters:
            return False
    return True


word = "napastak"
max_lives = 6
lives = max_lives
letters = []

print("🎮 Welcome to Hangman")
print("Type letters to guess the word")
print("Type 'quit' to exit\n")

while lives > 0 and not is_possible_to_create_word(letters, word):
    print("\nWord: ", end="")
    for c in word:
        if c in letters:
            print(c, end=" ")
        else:
            print("_", end=" ")

    print(f"\nLives: {'❤️' * lives}{'🖤' * (max_lives - lives)}")

    letter = input("Enter a letter: ").strip().lower()

    if letter == "quit":
        print("👋 Game exited")
        break

    if len(letter) != 1 or not letter.isalpha():
        print("⚠️ Please enter ONE letter only")
        continue

    if letter in letters:
        print("⚠️ You already used this letter")
        continue

    letters.append(letter)

    if letter not in word:
        lives -= 1
        print("❌ Wrong letter!")

# ---- GAME RESULT ----
if is_possible_to_create_word(letters, word):
    print(f"\n🎉 You WON! The word was '{word}'")
elif lives == 0:
    print(f"\n💀 You LOST! The word was '{word}'")
