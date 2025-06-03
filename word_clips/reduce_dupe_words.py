#!/usr/bin/env python3

import os
import re
from collections import defaultdict
import random
import sys

def get_starting_word(filename):
    """Extract the first word from a filename (letters only)"""
    match = re.match(r'^([a-zA-Z]+)', filename)
    return match.group(1).lower() if match else None

def delete_files_by_starting_word():
    # Group files by their starting word
    word_groups = defaultdict(list)
    
    # Get all files in current directory
    for filename in os.listdir('.'):
        if os.path.isfile(filename) and not filename.startswith('.'):
            starting_word = get_starting_word(filename)
            if starting_word:
                word_groups[starting_word].append(filename)
    
    if not word_groups:
        print("No eligible files found.")
        return
    
    # Process each group
    for word, files in word_groups.items():
        count = len(files)
        if count <= 1:
            print(f"• {word}: {count} file (keeping all)")
            continue
            
        # Determine how many to keep
        if count > 20:
            keep_count = 20
            delete_count = count - 20
            action = f"reducing to {keep_count}"
        else:
            keep_count = count - (count // 2)
            delete_count = count // 2
            action = f"keeping {keep_count} (deleting half)"
        
        print(f"• {word}: {count} files ({action})")
        
        # Randomly select files to delete
        files_to_delete = random.sample(files, delete_count)
        
        for file in files_to_delete:
            try:
                os.remove(file)
                print(f"  ▸ Deleted: {file}")
            except Exception as e:
                print(f"  ▸ Failed to delete {file}: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    print("File Cleanup Tool")
    print("=" * 40)
    print("Rules:")
    print("- >20 files: reduce to exactly 20")
    print("- 2-20 files: delete half (rounded down)")
    print("- Single files: always keep")
    print("- Hidden files (starting with '.'): always ignored")
    print("=" * 40)
    
    confirm = input("Type 'YES DELETE' to continue: ")
    if confirm.strip().upper() == 'YES DELETE':
        print("\nStarting cleanup...\n")
        delete_files_by_starting_word()
        print("\nCleanup complete.")
    else:
        print("\nOperation cancelled.")
