import curses
import random
from collections import Counter
from itertools import groupby
import statistics
import threading
import time

# ASCII Art for Simulators
ASCII_ART = {
    "menu": r"""
 __        __   _                            _          
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___    
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \   
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |  
    \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/   
                                                    """,
    "dice": r"""
 _____  
|_   _| 
  | |   
  | |   
 _| |_  
|_____| 
          
    """,
    "coin": r"""
  ____  
 / ___| 
| |     
| |___  
 \____| 
        
    """,
    "walk": r"""
 _    _      _                             
| |  | |    | |                            
| |  | | ___| | ___  ___  ___  _ __  ___  
| |/\| |/ _ \ |/ _ \/ __|/ _ \| '_ \/ __| 
\  /\  /  __/ |  __/\__ \ (_) | | | \__ \ 
 \/  \/ \___|_|\___||___/\___/|_| |_|___/ 
                                            
    """
}

def add_str_safe(stdscr, y, x, text, color_pair=0):
    """Safely adds a string to the curses window within terminal bounds."""
    height, width = stdscr.getmaxyx()
    if 0 <= y < height and 0 <= x < width:
        # Truncate the text if it exceeds the terminal width
        truncated_text = text[: width - x - 1]
        try:
            stdscr.addstr(y, x, truncated_text, curses.color_pair(color_pair))
        except curses.error:
            pass  # Ignore errors if the text cannot be added

def display_ascii_art(stdscr, art_key, y_offset=0, x_offset=0):
    """Displays ASCII art at the specified position."""
    art = ASCII_ART.get(art_key, "")
    for idx, line in enumerate(art.splitlines()):
        add_str_safe(stdscr, y_offset + idx, x_offset, line, color_pair=1)

def clear_screen(stdscr):
    """Clears the screen and refreshes."""
    stdscr.clear()
    stdscr.refresh()

def input_prompt(stdscr, prompt, y, x, max_length=10, color=3):
    """Handles user input with validation."""
    curses.echo()
    add_str_safe(stdscr, y, x, prompt, color_pair=color)
    stdscr.refresh()
    while True:
        try:
            user_input = stdscr.getstr(y, x + len(prompt), max_length).decode("utf-8")
            value = int(user_input)
            if value <= 0:
                raise ValueError
            curses.noecho()
            return value
        except ValueError:
            add_str_safe(stdscr, y + 1, x, "Invalid input. Please enter a positive integer.", 5)
            stdscr.refresh()
            time.sleep(1)
            # Clear the error message
            add_str_safe(stdscr, y + 1, x, " " * (len("Invalid input. Please enter a positive integer.") + 1), 5)
            stdscr.refresh()

def run_simulation_thread(target, args=()):
    """Runs a simulation in a separate thread."""
    simulation_thread = threading.Thread(target=target, args=args)
    simulation_thread.start()
    simulation_thread.join()

def dice_rolling_simulator(stdscr):
    """Simulates dice rolls with detailed analytics."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Display ASCII Art
    display_ascii_art(stdscr, "dice", y_offset=0, x_offset=(width // 2) - 10)

    # Input Prompts
    add_str_safe(stdscr, 10, 5, "=== Dice Rolling Simulator ===", 2)
    rolls = input_prompt(stdscr, "Enter the number of rolls: ", 12, 5)
    sides = input_prompt(stdscr, "Enter the number of sides on the dice: ", 13, 5)

    # Perform Rolls
    results = [random.randint(1, sides) for _ in range(rolls)]
    freq = Counter(results)
    avg = statistics.mean(results)
    median = statistics.median(results)
    try:
        modes = statistics.multimode(results)
        mode = ', '.join(map(str, modes))
    except statistics.StatisticsError:
        mode = "No unique mode"
    variance = statistics.variance(results) if rolls > 1 else 0
    std_dev = statistics.stdev(results) if rolls > 1 else 0

    # Display Results
    stdscr.clear()
    display_ascii_art(stdscr, "dice", y_offset=0, x_offset=(width // 2) - 10)
    add_str_safe(stdscr, 10, 5, "=== Dice Roll Results ===", 2)
    add_str_safe(stdscr, 12, 5, f"Number of Rolls: {rolls}", 3)
    add_str_safe(stdscr, 13, 5, f"Dice Sides: {sides}", 3)
    add_str_safe(stdscr, 14, 5, f"Average Roll: {avg:.2f}", 4)
    add_str_safe(stdscr, 15, 5, f"Median Roll: {median}", 4)
    add_str_safe(stdscr, 16, 5, f"Mode Roll(s): {mode}", 4)
    add_str_safe(stdscr, 17, 5, f"Variance: {variance:.2f}", 4)
    add_str_safe(stdscr, 18, 5, f"Standard Deviation: {std_dev:.2f}", 4)

    # Frequency Table with Histogram
    add_str_safe(stdscr, 20, 5, "Frequency Table:", 2)
    y = 21
    sorted_freq = sorted(freq.items())
    max_count = max(freq.values())
    histogram_scale = 40 / max_count if max_count > 0 else 1  # Scale histogram to fit width

    for num, count in sorted_freq:
        if y >= height - 4:
            add_str_safe(stdscr, y, 5, "...", 3)
            break
        bar = '*' * int(count * histogram_scale)
        add_str_safe(stdscr, y, 7, f"{num}: {count} | {bar}", 3)
        y += 1

    add_str_safe(stdscr, y + 1, 5, "Press any key to return to the main menu.", 5)
    stdscr.refresh()
    stdscr.getch()

def coin_flip_simulator(stdscr):
    """Simulates coin flips with detailed analytics."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Display ASCII Art
    display_ascii_art(stdscr, "coin", y_offset=0, x_offset=(width // 2) - 10)

    # Input Prompts
    add_str_safe(stdscr, 10, 5, "=== Coin Flip Simulator ===", 2)
    flips = input_prompt(stdscr, "Enter the number of flips: ", 12, 5)

    # Perform Flips
    results = [random.choice(["Heads", "Tails"]) for _ in range(flips)]
    freq = Counter(results)
    heads = freq.get("Heads", 0)
    tails = freq.get("Tails", 0)
    heads_pct = (heads / flips) * 100
    tails_pct = (tails / flips) * 100
    streaks = [len(list(group)) for _, group in groupby(results)]
    longest_streak = max(streaks) if streaks else 0
    total_streaks = len(streaks)

    # Display Results
    stdscr.clear()
    display_ascii_art(stdscr, "coin", y_offset=0, x_offset=(width // 2) - 10)
    add_str_safe(stdscr, 10, 5, "=== Coin Flip Results ===", 2)
    add_str_safe(stdscr, 12, 5, f"Number of Flips: {flips}", 3)
    add_str_safe(stdscr, 13, 5, f"Heads: {heads} ({heads_pct:.2f}%)", 4)
    add_str_safe(stdscr, 14, 5, f"Tails: {tails} ({tails_pct:.2f}%)", 4)
    add_str_safe(stdscr, 15, 5, f"Longest Streak: {longest_streak}", 4)
    add_str_safe(stdscr, 16, 5, f"Total Streaks: {total_streaks}", 4)

    # Streak Analysis
    add_str_safe(stdscr, 18, 5, "Streaks Details:", 2)
    y = 19
    for idx, streak_length in enumerate(streaks, start=1):
        if y >= height - 4:
            add_str_safe(stdscr, y, 5, "...", 3)
            break
        add_str_safe(stdscr, y, 7, f"Streak {idx}: {streak_length}", 3)
        y += 1

    # Probability Distribution Comparison
    theoretical_heads_pct = 50.0
    theoretical_tails_pct = 50.0
    add_str_safe(stdscr, y + 1, 5, "Probability Distribution:", 2)
    add_str_safe(stdscr, y + 2, 7, f"Theoretical Heads: {theoretical_heads_pct:.2f}%", 3)
    add_str_safe(stdscr, y + 3, 7, f"Experimental Heads: {heads_pct:.2f}%", 3)
    add_str_safe(stdscr, y + 4, 7, f"Theoretical Tails: {theoretical_tails_pct:.2f}%", 3)
    add_str_safe(stdscr, y + 5, 7, f"Experimental Tails: {tails_pct:.2f}%", 3)

    add_str_safe(stdscr, y + 7, 5, "Press any key to return to the main menu.", 5)
    stdscr.refresh()
    stdscr.getch()

def random_walk_simulator(stdscr):
    """Simulates a random walk in one dimension with detailed analytics."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Display ASCII Art
    display_ascii_art(stdscr, "walk", y_offset=0, x_offset=(width // 2) - 10)

    # Input Prompts
    add_str_safe(stdscr, 10, 5, "=== Random Walk Simulator ===", 2)
    steps = input_prompt(stdscr, "Enter the number of steps: ", 12, 5)

    # Perform Random Walk
    position = 0
    positions = [position]
    for _ in range(steps):
        step = random.choice([-1, 1])
        position += step
        positions.append(position)

    # Analytics
    max_dist = max(abs(pos) for pos in positions)
    avg_dist = statistics.mean(abs(pos) for pos in positions)
    final_pos = positions[-1]
    displacement = final_pos
    total_displacement = sum(abs(pos) for pos in positions)

    # Display Results
    stdscr.clear()
    display_ascii_art(stdscr, "walk", y_offset=0, x_offset=(width // 2) - 10)
    add_str_safe(stdscr, 10, 5, "=== Random Walk Results ===", 2)
    add_str_safe(stdscr, 12, 5, f"Number of Steps: {steps}", 3)
    add_str_safe(stdscr, 13, 5, f"Final Position: {final_pos}", 4)
    add_str_safe(stdscr, 14, 5, f"Total Displacement: {total_displacement}", 4)
    add_str_safe(stdscr, 15, 5, f"Net Displacement: {displacement}", 4)
    add_str_safe(stdscr, 16, 5, f"Farthest Distance from Origin: {max_dist}", 4)
    add_str_safe(stdscr, 17, 5, f"Average Distance from Origin: {avg_dist:.2f}", 4)

    # Step-by-Step Positions (ASCII Path)
    add_str_safe(stdscr, 19, 5, "Step-by-Step Positions:", 2)
    y = 20
    pos_display_limit = height - y - 4
    step_display = min(steps + 1, pos_display_limit)
    for i in range(step_display):
        if y >= height - 4:
            break
        pos = positions[i]
        # Simple visualization: position scaled to fit width
        scale = (width - 20) // max(1, max(abs(pos) for pos in positions))
        pos_visual = ' ' * (10 + pos * scale) + '*'
        add_str_safe(stdscr, y, 7, f"Step {i}: Position {pos} {pos_visual}", 3)
        y += 1
    if steps + 1 > pos_display_limit:
        add_str_safe(stdscr, y, 7, f"...and {steps +1 - pos_display_limit} more steps", 3)

    add_str_safe(stdscr, y + 1, 5, "Press any key to return to the main menu.", 5)
    stdscr.refresh()
    stdscr.getch()

def main_menu(stdscr):
    """Main menu for the simulation program."""
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # For ASCII Art
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # For Titles
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # For Prompts
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # For Results
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)     # For Errors

    curses.curs_set(0)  # Hide cursor

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Display ASCII Art for Menu
        display_ascii_art(stdscr, "menu", y_offset=0, x_offset=(width // 2) - 20)

        # Menu Options
        add_str_safe(stdscr, 10, 5, "=== Simulation Menu ===", 2)
        add_str_safe(stdscr, 12, 5, "1. Dice Rolling Simulator", 3)
        add_str_safe(stdscr, 13, 5, "2. Coin Flip Simulator", 3)
        add_str_safe(stdscr, 14, 5, "3. Random Walk Simulator", 3)
        add_str_safe(stdscr, 16, 5, "Press 'q' to quit.", 1)
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('1'):
            run_simulation_thread(dice_rolling_simulator, args=(stdscr,))
        elif key == ord('2'):
            run_simulation_thread(coin_flip_simulator, args=(stdscr,))
        elif key == ord('3'):
            run_simulation_thread(random_walk_simulator, args=(stdscr,))
        elif key in [ord('q'), ord('Q')]:
            break  # Exit the program

def main():
    """Entry point for the simulation program."""
    try:
        curses.wrapper(main_menu)
    except Exception as e:
        # In case of unexpected errors, ensure the terminal state is restored
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
