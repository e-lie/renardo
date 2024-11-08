import os
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
from urllib.parse import urljoin, quote
import pudb

# Configure Jinja environment
env = Environment(loader=FileSystemLoader(searchpath=''), autoescape=select_autoescape(['html']))

# Jinja HTML template for folder index
template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Index of {{ current_dir }}</title>
</head>
<body>
    <h1>Index of {{ current_dir }}</h1>
    <ul>
        {% if parent_dir %}
            <li><a href="{{ parent_dir }}">.. (Parent Directory)</a></li>
        {% endif %}
        {% for folder in folders %}
            <li><a href="{{ base_url }}{{current_dir}}/{{ folder }}">{{ folder }}/</a></li>
        {% endfor %}
        {% for file in files %}
            <li><a href="{{ base_url }}{{current_dir}}/{{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

# Compile the template
template = env.from_string(template_content)

def generate_index_html(base_dir, base_url):
    for root, dirs, files in os.walk(base_dir):
        # pudb.set_trace()
        # Determine the folder name (we use index.html for each folder)
        folder_name = os.path.basename(root) or "root"  # "root" for base directory
        index_filename = "index.html"  # Always name the file index.html
        index_file_path = os.path.join(root, index_filename)

        # Get the relative path of the current directory from base_dir
        current_dir = os.path.relpath(root, base_dir)

        # Calculate the parent directory link (point to its prefixed index.html)
        if current_dir == ".":
            parent_dir = None  # No parent link for the base directory
        else:
            parent_folder_name = os.path.basename(os.path.dirname(root)) or "root"
            parent_dir = os.path.join(base_url, os.path.relpath(os.path.join(root, ".."), base_dir))

        # URL encode folder and file names
        encoded_dirs = [quote(d) for d in sorted(dirs)]
        encoded_files = [quote(f) for f in sorted(files)]

        # Render the HTML content
        html_content = template.render(
            current_dir=current_dir,
            parent_dir=parent_dir,
            folders=encoded_dirs,
            files=encoded_files,
            base_url=base_url
        )

        # Write the HTML file
        with open(index_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Generated {index_file_path}")


base_directory = "./samples"
base_url = 'http://localhost:8000/' 

generate_index_html(base_directory, base_url)
