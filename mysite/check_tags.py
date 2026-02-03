import os
import re

def check_templates(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Simple stack based check
                    stack = []
                    # Find all {% if ... %}, {% for ... %}, {% block ... %}, {% endif %}, {% endfor %}, {% endblock %}
                    tags = re.findall(r'{%\s*(if|for|block|endif|endfor|endblock)\b.*?%}', content)
                    errors = []
                    for tag in tags:
                        if tag in ['if', 'for', 'block']:
                            stack.append((tag, path))
                        elif tag.startswith('end'):
                            expected = tag[3:]
                            if not stack:
                                errors.append(f"Unexpected {{% {tag} %}} in {path}")
                            else:
                                last_tag, last_path = stack.pop()
                                if last_tag != expected:
                                    errors.append(f"Mismatched {{% {tag} %}} for {{% {last_tag} %}} in {path}")
                    
                    for tag, path in stack:
                        errors.append(f"Unclosed {{% {tag} %}} in {path}")
                    
                    if errors:
                        for err in errors:
                            print(err)

if __name__ == "__main__":
    check_templates('l:/PYTHON/PROJECTS/dpits-cms/mysite/templates')
    check_templates('l:/PYTHON/PROJECTS/dpits-cms/mysite/main/templates')
    check_templates('l:/PYTHON/PROJECTS/dpits-cms/mysite/news/templates')
    check_templates('l:/PYTHON/PROJECTS/dpits-cms/mysite/portfolio/templates')
    check_templates('l:/PYTHON/PROJECTS/dpits-cms/mysite/services/templates')
    check_templates('l:/PYTHON/PROJECTS/dpits-cms/mysite/reviews/templates')
    check_templates('l:/PYTHON/PROJECTS/dpits-cms/mysite/feedback/templates')
