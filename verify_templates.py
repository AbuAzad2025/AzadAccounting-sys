import os
import sys
from flask import Flask
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

# إعداد تطبيق Flask وهمي
app = Flask(__name__)
template_dir = os.path.join(os.getcwd(), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

def check_templates():
    print("🔍 Starting Template Syntax Verification...")
    print(f"📂 Template Directory: {template_dir}")
    
    errors = []
    checked_count = 0
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, template_dir)
                # استبدال الشرطات المائلة العكسية في Windows
                rel_path = rel_path.replace('\\', '/')
                
                try:
                    # محاولة تحميل وتجميع القالب
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    env.parse(source)
                    checked_count += 1
                    # print(f"✅ OK: {rel_path}")
                except TemplateSyntaxError as e:
                    errors.append(f"❌ Syntax Error in {rel_path}: {e.message} at line {e.lineno}")
                except Exception as e:
                    errors.append(f"❌ Error in {rel_path}: {str(e)}")

    print(f"\n📊 Summary:")
    print(f"   Checked: {checked_count} templates")
    print(f"   Errors:  {len(errors)}")
    
    if errors:
        print("\n⚠️  TEMPLATE ERRORS FOUND:")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("\n✅ All templates are syntactically CORRECT!")
        sys.exit(0)

if __name__ == "__main__":
    check_templates()
