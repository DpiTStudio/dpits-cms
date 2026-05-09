import re
import sys

try:
    with open('temp_error.html', encoding='utf-16') as f:
        html = f.read()
    
    m_title = re.search(r'<title>(.*?)</title>', html, re.S)
    print('Title:', m_title.group(1).strip() if m_title else 'None')
    
    m_exc = re.search(r'<pre class="exception_value">(.*?)</pre>', html, re.S)
    print('Exception:', m_exc.group(1).strip() if m_exc else 'None')
    
    m_loc = re.search(r'<th>Exception Location:</th>\s*<td>(.*?)</td>', html, re.S)
    print('Location:', m_loc.group(1).strip() if m_loc else 'None')
except Exception as e:
    print(e)
