import os
import re
import shutil

def organize_mp3s_by_first_word(directory):
    """
    Organizes MP3 files into folders based on the first word of their filename,
    with more flexible word matching.
    """
    # Compile regex pattern to match the first alphabetic word
    # This will match any sequence of letters at the start or after non-letters
    pattern = re.compile(r'^([^0-9_]+)')
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith('.mp3'):
            filepath = os.path.join(directory, filename)
            
            # Skip directories (only process files)
            if not os.path.isfile(filepath):
                continue
            
            # Match the first alphabetic word
            match = pattern.match(filename)
            if match:
                first_word = match.group(1).lower()  # Use lowercase for consistency
                
                # Create folder path
                folder_path = os.path.join(directory, first_word)
                
                # Create folder if it doesn't exist
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                # Move file to the folder
                destination = os.path.join(folder_path, filename)
                shutil.move(filepath, destination)
                print(f"Moved '{filename}' to '{first_word}/'")
            else:
                print(f"Skipping '{filename}' - no valid first word found")

if __name__ == "__main__":
    target_directory = input("Enter the directory path to organize: ").strip()
    
    # Validate directory
    if not os.path.isdir(target_directory):
        print("Error: The specified directory does not exist.")
    else:
        organize_mp3s_by_first_word(target_directory)
        print("Organization complete!")
