# Skill: Comment the Code
# This program demonstrates loops, selection, libraries, and string manipulation.

import random  # Skill: Use Program Library Functions

def get_winner(player_move, computer_move):
    """
    Compares player and computer moves to determine the winner.
    (This is a function docstring, as per coding standard 1.4)
    
    Args:
        player_move (str): The player's choice ('rock', 'paper', 'scissors')
        computer_move (str): The computer's choice

    Returns:
        str: 'draw', 'player', or 'computer'
    """
    
    # Skill: Use Selection Structures (if/elif/else)
    if player_move == computer_move:
        return "draw"
    
    # Skill: Use Data Types, Operators (==, and, or)
    elif (player_move == 'rock' and computer_move == 'scissors') or \
         (player_move == 'scissors' and computer_move == 'paper') or \
         (player_move == 'paper' and computer_move == 'rock'):
        return "player"
    else:
        return "computer"

def main():
    """Main game loop for Rock-Paper-Scissors."""
    
    # Skill: Apply Variables and Variable Scope ('options', 'playing')
    options = ['rock', 'paper', 'scissors']
    playing = True

    # Skill: Use Loop Structures (while)
    while playing:
        player_choice = ""
        
        # Loop until valid input is received
        while player_choice not in options:
            # Skill: Perform String Manipulation (input(),.lower())
            player_choice = input("Enter your move (rock, paper, or scissors): ").lower()
            
            if player_choice not in options:
                print("Error: Invalid move. Please try again.")

        # Use library function to get computer's move
        computer_choice = random.choice(options)

        print(f"You chose: {player_choice}")
        print(f"Computer chose: {computer_choice}")

        # Call function to get winner
        winner = get_winner(player_choice, computer_choice)

        # Display result
        if winner == 'draw':
            print("It's a draw!")
        elif winner == 'player':
            print("You win!")
        else:
            print("Computer wins!")

        # Skill: Use Sequence Structures (code runs in order)
        play_again = input("Play again? (y/n): ").lower()
        if play_again!= 'y':
            playing = False

    print("Thanks for playing!")

# Skill: Apply Basic Language Syntax Rules (main entry point)
if __name__ == "__main__":
    main()