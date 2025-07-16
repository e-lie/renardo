#!/usr/bin/env python3
"""Script to convert multiline docstrings to oneliners in reaside module."""

import os
import re
import glob

def convert_multiline_docstrings(file_path):
    """Convert multiline docstrings to oneliners in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match multiline docstrings
    # This pattern matches:
    # - Opening triple quotes
    # - First line (the summary)
    # - Any amount of content including Parameters, Returns, etc.
    # - Closing triple quotes
    pattern = r'"""([^"]*?)\n(?:.*?)\n\s*"""'
    
    def replace_docstring(match):
        # Get the first line which is typically the summary
        first_line = match.group(1).strip()
        # If the first line is empty or contains just whitespace, 
        # we need to find the actual summary
        if not first_line:
            # Try to find the first non-empty line in the docstring
            full_match = match.group(0)
            lines = full_match.split('\n')
            for line in lines[1:]:  # Skip the opening """
                cleaned = line.strip()
                if cleaned and not cleaned.startswith('"""') and not cleaned.startswith('Parameters') and not cleaned.startswith('Returns') and not cleaned.startswith('Raises'):
                    first_line = cleaned
                    break
        
        # Clean up the first line and ensure it ends with a period if it's a sentence
        if first_line:
            if not first_line.endswith('.') and not first_line.endswith('?') and not first_line.endswith('!'):
                first_line += '.'
            return f'"""{first_line}"""'
        else:
            return '"""Function description."""'
    
    # Apply the replacement
    modified_content = re.sub(pattern, replace_docstring, content, flags=re.DOTALL)
    
    # Write back the modified content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    return modified_content != content

def main():
    """Main function to convert docstrings in all Python files."""
    reaside_path = "/home/elie/Bureau/Livecoding/02 - renardo dev/renardo/src/renardo/reaper_backend/reaside"
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(reaside_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    
    modified_files = []
    for file_path in python_files:
        try:
            if convert_multiline_docstrings(file_path):
                print(f"Modified: {file_path}")
                modified_files.append(file_path)
            else:
                print(f"No changes: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nTotal files modified: {len(modified_files)}")
    for file_path in modified_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    main()