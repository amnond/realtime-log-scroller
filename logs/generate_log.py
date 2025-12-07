import random
import time
import string
import os

# --- Helper Functions (Same as before) ---

def generate_gibberish(length=10):
    """Generates a random string of lowercase letters."""
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def generate_random_color():
    """Generates a random hexadecimal color string (e.g., #FF9900)."""
    return '#%06x' % random.randint(0, 0xFFFFFF)

counter = 0
def generate_random_html_line():
    """Generates one of the two specified random HTML lines."""
    global counter
    choice = random.randint(1, 2)
    gibberish = generate_gibberish(random.randint(20, 50))
    counter += 1
    
    if choice == 1:
        # 1. A div with random height, color, and font size.
        height = random.randint(50, 190)
        color = generate_random_color()
        font_size = random.randint(12, 30) # Font size in pixels

        style = (
            f"height: {height}px; "
            f"background-color: {color}; "
            f"font-size: {font_size}px; "
            "margin: 5px; padding: 5px; border: 1px solid #333; color: #333;" # Added text color
        )
        return f'<div style="{style}">[{counter}] {gibberish}</div>'

    else:
        # 2. A header with gibberish text (H1 to H5).
        header_level = random.randint(1, 5)
        tag = f'h{header_level}'
        
        # Add a light margin for spacing headers
        style = "margin: 5px; padding: 5px;"
        return f'<{tag} style="{style}">[{counter}] {gibberish.upper()}</{tag}>'

# --- Main Generation and File Writing Function ---

def generate_html_stream_to_file(filename="random_stream.html"):
    """
    Continuously generates HTML lines and appends them to a file.
    It also ensures the file is wrapped in proper HTML structure.
    """
    print(f"--- Starting HTML Line Generator. Outputting to **{filename}** ---")
    print("Press Ctrl+C to stop the process.")

    # 1. Create the initial, well-formed HTML file structure
    initial_content = ''
    
    # Write the header content, overwriting the file if it exists
    with open(filename, 'w') as f:
        f.write(initial_content.strip())
    
    line_count = 0
    while True:
        try:
            html_line = generate_random_html_line()
            
            # 2. Append the new line to the file
            # We open the file in 'a' (append) mode
            with open(filename, 'a') as f:
                f.write(f"    {html_line}\n")
            
            line_count += 1
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp} | #{line_count}] Wrote line to file.")
            
            time.sleep(0.2) # Wait for one second
            
        except KeyboardInterrupt:
            # 3. Finalize the HTML file structure upon stopping
            print("\n--- Generator stopped. Finalizing HTML file. ---")
                
            # Offer to open the file
            print(f"File **{filename}** is complete. Open it in your web browser to view the result.")
            break

if __name__ == "__main__":
    generate_html_stream_to_file()