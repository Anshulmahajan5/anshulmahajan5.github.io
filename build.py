import os
import json
import re

PROJECTS_DIR = 'projects'
INDEX_FILE = 'index.html'

# Clean template for bento grid injection
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

    # Standard Sorting: 01, 02, 03... (Lowest number = Top of site)
    folders = sorted([f for f in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, f))])
    
    print(f"Found {len(folders)} project folders. Starting build...")

    for folder in folders:
        info_path = os.path.join(PROJECTS_DIR, folder, 'info.json')
        
        # We ONLY open the .json file to prevent huge file size errors
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Process fields into tags
                    fields_raw = data.get('fields', '3D Art')
                    field_list = [s.strip() for s in fields_raw.split(',')]
                    field_spans = "".join([f'<span class="bento-field">{s}</span>' for s in field_list])
                    
                    # Ensure images are simple strings/paths
                    main_image = data.get('image', '')
                    all_imgs = data.get('all_images', main_image)
                    
                    generated_html += html_template.format(
                        title=data.get('title', 'Untitled'),
                        fields=fields_raw,
                        description=data.get('description', ''),
                        year=data.get('year', '2026'),
                        link=data.get('link', '#'),
                        image=main_image,
                        all_images=all_imgs,
                        field_spans=field_spans
                    )
            except Exception as e:
                print(f"Skipping folder {folder} due to error: {e}")

    # Read the current index.html
    if not os.path.exists(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found.")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Search and replace between markers
    pattern = r'()(.*?)()'
    replacement = r'\1\n' + generated_html + r'\n\3'
    
    # Use re.DOTALL to match across multiple lines
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Write the clean, updated HTML back
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Build successful! index.html updated with {len(folders)} projects.")

if __name__ == "__main__":
    build()
