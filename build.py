import os
import json
import re

PROJECTS_DIR = 'projects'
INDEX_FILE = 'index.html'

# Template matching the bento grid structure
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
    <div class="bento-fields">
      {field_spans}
    </div>
    <div class="bento-title">{title}</div>
  </div>
  <div class="bento-arrow"><i class="fas fa-expand"></i></div>
</div>
"""

def build():
    generated_html = ""
    if not os.path.exists(PROJECTS_DIR):
        print("Error: 'projects' directory not found.")
        return

    # STANDARD SORTING (01, 02, 03...)
    # Folder 01 appears at the TOP.
    folders = sorted([f for f in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, f))])
    
    for folder in folders:
        info_path = os.path.join(PROJECTS_DIR, folder, 'info.json')
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                fields_raw = data.get('fields', '3D Art')
                field_spans = "".join([f'<span class="bento-field">{s.strip()}</span>' for s in fields_raw.split(',')])
                all_imgs = data.get('all_images', data.get('image', ''))
                
                generated_html += html_template.format(
                    title=data.get('title', 'Untitled'),
                    fields=fields_raw,
                    description=data.get('description', ''),
                    year=data.get('year', '2026'),
                    link=data.get('link', '#'),
                    image=data.get('image', ''),
                    all_images=all_imgs,
                    field_spans=field_spans
                )

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'()(.*?)()'
    replacement = r'\1\n' + generated_html + r'\n\3'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Success: Injected {len(folders)} projects.")

if __name__ == "__main__":
    build()
