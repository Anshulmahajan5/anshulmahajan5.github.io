import os
import json
import re

PROJECTS_DIR = 'projects'
INDEX_FILE = 'index.html'

html_template = """
<div class="bento-item reveal"
     data-title="{title}"
     data-fields="{fields}"
     data-description="{description}"
     data-year="{year}"
     data-behance-url="{link}"
     data-images="{all_images}">
  <img class="bento-media" src="{image}" alt="{title}" loading="lazy">
  <div class="bento-overlay">
    <div class="bento-fields">{field_spans}</div>
    <div class="bento-title">{title}</div>
  </div>
  <div class="bento-arrow"><i class="fas fa-expand"></i></div>
</div>
"""

def build():
    generated_html = ""
    if not os.path.exists(PROJECTS_DIR):
        print(f"No '{PROJECTS_DIR}' directory found. Nothing to inject.")
        return

    folders = sorted([
        f for f in os.listdir(PROJECTS_DIR)
        if os.path.isdir(os.path.join(PROJECTS_DIR, f))
    ])

    for folder in folders:
        info_path = os.path.join(PROJECTS_DIR, folder, 'info.json')
        if not os.path.exists(info_path):
            print(f"Skipping '{folder}': no info.json found.")
            continue

        with open(info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Guard: image value must be a short relative path, never raw binary/base64 data.
        # A valid relative path is under 500 chars and never starts with "data:".
        image_path = data.get('image', '')
        if image_path.startswith('data:') or len(image_path) > 500:
            print(f"Skipping '{folder}': 'image' field looks like embedded data, not a file path.")
            continue

        fields     = data.get('fields', '')
        field_spans = ''.join(
            f'<span class="bento-field">{s.strip()}</span>'
            for s in fields.split(',') if s.strip()
        )

        generated_html += html_template.format(
            title       = data.get('title',       'Untitled'),
            fields      = fields,
            description = data.get('description', ''),
            year        = data.get('year',        '2025'),
            link        = data.get('link',        '#'),
            image       = image_path,
            all_images  = data.get('all_images',  image_path),
            field_spans = field_spans,
        )

    # Read the template — strip Windows \r\n so the regex works on any runner
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read().replace('\r\n', '\n').replace('\r', '\n')

    # Match exactly between the two marker comments and replace the contents.
    # \1 keeps <!-- PROJECTS_START -->, \3 keeps <!-- PROJECTS_END -->.
    pattern = r'(<!-- PROJECTS_START -->)(.*?)(<!-- PROJECTS_END -->)'
    replacement = r'\1' + '\n' + generated_html + '\n    ' + r'\3'
    new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if n == 0:
        print("ERROR: Markers <!-- PROJECTS_START --> and <!-- PROJECTS_END --> not found in index.html.")
        print("Make sure both comment lines exist exactly as shown in the index.html grid section.")
        raise SystemExit(1)

    with open(INDEX_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    project_count = generated_html.count('class="bento-item')
    print(f"Build complete. {project_count} project card(s) injected into {INDEX_FILE}.")

if __name__ == '__main__':
    build()
