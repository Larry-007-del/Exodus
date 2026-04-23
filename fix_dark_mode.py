"""
Batch fix dark mode classes across all Exodus templates.
Adds dark:text-white or dark:text-gray-300 to common text classes missing their dark variants.
"""
import os
import re

TEMPLATES_DIR = r"d:\Exodus\attendance_system_master\templates"

# Patterns to fix: (search, replace)
REPLACEMENTS = [
    # Headings - text-gray-900 without dark:text-white
    (r'text-gray-900(?![\s\S]{0,30}dark:text)', 'text-gray-900 dark:text-white'),
    # Labels & body text - text-gray-700 without dark:text 
    (r'text-gray-700(?![\s\S]{0,30}dark:text)', 'text-gray-700 dark:text-gray-300'),
    # Sub text - text-gray-800 without dark:text
    (r'text-gray-800(?![\s\S]{0,30}dark:text)', 'text-gray-800 dark:text-gray-200'),
]

# Only fix within class="" attributes
def fix_class_attrs(content):
    """Fix dark mode classes within class attributes only."""
    
    def replace_in_class(match):
        class_val = match.group(1)
        
        # text-gray-900 -> add dark:text-white if not present
        if 'text-gray-900' in class_val and 'dark:text-' not in class_val:
            class_val = class_val.replace('text-gray-900', 'text-gray-900 dark:text-white')
        
        # text-gray-700 -> add dark:text-gray-300 if not present
        if 'text-gray-700' in class_val and 'dark:text-' not in class_val:
            class_val = class_val.replace('text-gray-700', 'text-gray-700 dark:text-gray-300')
        
        # text-gray-800 -> add dark:text-gray-200 if not present
        if 'text-gray-800' in class_val and 'dark:text-' not in class_val:
            class_val = class_val.replace('text-gray-800', 'text-gray-800 dark:text-gray-200')
            
        # bg-white without dark:bg
        if 'bg-white' in class_val and 'dark:bg-' not in class_val and 'bg-white/' not in class_val:
            class_val = class_val.replace('bg-white', 'bg-white dark:bg-gray-800')

        # border-gray-200 without dark:border
        if 'border-gray-200' in class_val and 'dark:border-' not in class_val and 'border-gray-200/' not in class_val:
            class_val = class_val.replace('border-gray-200', 'border-gray-200 dark:border-gray-700')

        # border-gray-100 without dark:border
        if 'border-gray-100' in class_val and 'dark:border-' not in class_val:
            class_val = class_val.replace('border-gray-100', 'border-gray-100 dark:border-gray-700')
            
        return f'class="{class_val}"'
    
    # Match class="..." attributes (handles multi-line with re.DOTALL per match)
    return re.sub(r'class="([^"]*)"', replace_in_class, content)


# Skip standalone auth pages (login.html, register.html, password_reset*.html) 
# as they have their own dark theme via glassmorphism
SKIP_FILES = {'login.html', 'register.html', 'password_reset.html', 
              'password_reset_done.html', 'password_reset_confirm.html', 
              'password_reset_complete.html'}

changed_files = []
for root, dirs, files in os.walk(TEMPLATES_DIR):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        if fname in SKIP_FILES:
            continue
            
        filepath = os.path.join(root, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        fixed = fix_class_attrs(original)
        
        if fixed != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
            changed_files.append(os.path.relpath(filepath, TEMPLATES_DIR))

print(f"Fixed {len(changed_files)} files:")
for f in sorted(changed_files):
    print(f"  - {f}")
