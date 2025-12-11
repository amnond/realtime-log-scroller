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

import random

def generate_random_sentence():
    """
    Generates a random sentence based on predefined Part-of-Speech templates
    and a corresponding dictionary of words.

    Returns:
        str: A grammatically structured, random sentence.
    """
    # --- 1. Word Bank (Part-of-Speech Dictionary) ---
    # Define your word bank. Keys are the Part-of-Speech (POS) tags.
    # N = Noun, V = Verb, ADJ = Adjective, ADV = Adverb, DET = Determiner (Article/Quantifier)
    word_bank = {
        'DET': ['a', 'the', 'some', 'every', 'no', 'one'],
        'N': ['dog', 'cat', 'programmer', 'coffee', 'mountain', 'book', 'pizza', 'elephant', 'galaxy'],
        'V': ['runs', 'sleeps', 'codes', 'eats', 'climbs', 'reads', 'jumps', 'rotates', 'plunges'],
        'ADJ': ['fluffy', 'sleepy', 'smart', 'delicious', 'high', 'blue', 'quick', 'finicky', 'irritable', 'lousy', 'ghostly'],
        'ADV': ['quickly', 'slowly', 'eagerly', 'happily', 'loudly', 'silently', 'peacefully', 'mightily'],
        'CONJ':['and', 'while', 'but']
    }

    # --- 2. Sentence Templates ---
    # Define a list of grammatically valid Part-of-Speech sequences.
    # Each list item is a template.
    sentence_templates = [
        ['DET', 'ADJ', 'N', 'ADV', 'V'],        # Example: The fluffy cat quickly sleeps.
        ['DET', 'N', 'V', 'DET', 'N'],          # Example: A programmer codes a book.
        [],               # Example: Every mountain climbs slowly.
        ['DET', 'ADJ', 'N', 'V'],                # Example: Sleepy dog jumps
        ['DET', 'N', 'V', 'DET', 'N', 'CONJ', 'DET', 'N', 'V', 'ADV']
    ]
    # 

    # --- 3. Selection and Generation ---

    # 3.1. Choose a random template
    template = random.choice(sentence_templates)

    # 3.2. Generate the sentence by replacing POS tags with random words
    sentence_words = []
    for pos_tag in template:
        if pos_tag in word_bank:
            # Select a random word for the current POS tag
            word = random.choice(word_bank[pos_tag])
            sentence_words.append(word)
        elif pos_tag == 'PUNCT':
            # Handle punctuation separately to avoid a leading space
            punctuation = random.choice(word_bank['PUNCT'])
            # Remove the space before the punctuation
            if sentence_words:
                sentence_words[-1] = sentence_words[-1] + punctuation
        else:
            # Fallback for an unrecognized tag
            sentence_words.append(f'[{pos_tag} missing]')


    # 3.3. Join the words into a single sentence string
    sentence = " ".join(sentence_words)

    # 3.4. Final polish: Capitalize the first letter
    if sentence:
        sentence = sentence[0].upper() + sentence[1:]

    return sentence + ". "

def generate_random_sentences():
    result = ""
    for i in range(random.randint(5, 15)):
        result += generate_random_sentence()
    return result
    
counter = 0
def generate_random_html_line():
    """Generates one of the two specified random HTML lines."""
    global counter
    choice = random.randint(1, 2)
    random_sentences = generate_random_sentences()
    counter += 1

    color = generate_random_color()
    height = random.randint(50, 190)
    
    if choice == 1:
        # 1. A div with random height, color, and font size.
        font_size = random.randint(12, 30) # Font size in pixels

        style = (
            f"background-color: {color}; "
            f"font-size: {font_size}px; "
            "margin: 5px; padding: 5px; border: 1px solid #333; color: #333;" # Added text color
        )
        return f'<div style="{style}">[{counter}] {random_sentences}</div>'

    else:
        # 2. A header with gibberish text (H1 to H5).
        header_level = random.randint(1, 5)
        tag = f'h{header_level}'

        sentence = generate_random_sentence()
        style = (
          "margin: 5px; padding: 5px;"
          f"height: {height}px; "
          f"background-color: {color}; "
        )
        
        return f'<{tag} style="{style}">[{counter}] {sentence.upper()}</{tag}>'

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