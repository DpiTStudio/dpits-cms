import os
import re
import sys

def bundle_css():
    # Base paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_html_path = os.path.join(current_dir, 'templates', 'layout', 'css.html')
    static_dir = os.path.join(current_dir, 'static')
    output_bundle_path = os.path.join(static_dir, 'css', 'bundle.min.css')

    if not os.path.exists(css_html_path):
        print(f"Error: css.html not found at {css_html_path}")
        sys.exit(1)

    print("Reading css.html to parse CSS stylesheet loading order...")
    with open(css_html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all stylesheet links: {% static 'css/...' %}
    # Format: {% static 'css/00_variables/variables.css' %}
    pattern = re.compile(r"{%\s*static\s+['\"](css/[^'\"]+css)['\"]\s*%}")
    css_files = pattern.findall(content)

    if not css_files:
        print("Warning: No CSS file links found using regular static template tag in css.html.")
        # Try a more relaxed pattern
        pattern_fallback = re.compile(r"href=['\"]{% static ['\"](css/[^'\"]+)['\"] %}")
        css_files = pattern_fallback.findall(content)

    print(f"Found {len(css_files)} CSS files to bundle:")
    
    bundled_content = []
    
    for css_file in css_files:
        # Ignore already bundled file if referenced
        if 'bundle.min.css' in css_file:
            continue
            
        full_path = os.path.join(static_dir, css_file)
        if not os.path.exists(full_path):
            # Try without static prefix if it's already solved
            full_path = os.path.join(current_dir, css_file)
            
        if os.path.exists(full_path):
            print(f" - Processing {css_file}")
            with open(full_path, 'r', encoding='utf-8') as f_css:
                css_data = f_css.read()
                
            # Basic Minification
            # Remove comments
            css_data = re.sub(r'/\*.*?\*/', '', css_data, flags=re.DOTALL)
            # Remove whitespace around selectors/properties
            css_data = re.sub(r'\s*([\{\};:,])\s*', r'\1', css_data)
            # Remove duplicate spaces and line breaks
            css_data = re.sub(r'\s+', ' ', css_data)
            
            bundled_content.append(f"/* Source: {css_file} */\n{css_data.strip()}\n")
        else:
            print(f" - WARNING: File not found: {full_path}")

    if bundled_content:
        # Ensure target directory exists
        os.makedirs(os.path.dirname(output_bundle_path), exist_ok=True)
        
        # Write output file
        with open(output_bundle_path, 'w', encoding='utf-8') as f_out:
            f_out.write("".join(bundled_content))
            
        print(f"\nSUCCESS! Bundled {len(bundled_content)} CSS files into {output_bundle_path}")
        print(f"Size of bundle: {os.path.getsize(output_bundle_path) / 1024:.2f} KB")
    else:
        print("Error: No CSS files processed.")

if __name__ == '__main__':
    bundle_css()
