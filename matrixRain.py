import random
import time
import os

# Characters to display
characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-=_+[]{}|;:',.<>?/\\"

# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Main function to display the matrix rain effect
def matrix_rain():
    width = 80
    print("\033[32m")  # Set text color to green
    while True:
        line = ''.join(random.choice(characters) for _ in range(width))
        print(line)
        time.sleep(0.05)
        clear_screen()

if __name__ == "__main__":
    matrix_rain()
