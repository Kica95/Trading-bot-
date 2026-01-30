import os
from datetime import datetime

def save_string_to_file(content, file_path):
    """
    Saves a large string to a text file, creating any missing directories.

    :param content: The string to save.
    :param file_path: The path (with filename) where the content will be saved.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def append_to_file(text: str, filename: str):
    """
    Appends the given text to a file.
    Creates the file if it doesn't exist.

    :param text: The string to append
    :param filename: Path to the text file
    """
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception as e:
        print(f"Error writing to file: {e}")
