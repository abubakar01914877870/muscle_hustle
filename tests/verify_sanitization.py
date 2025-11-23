import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.utils.security import sanitize_blog_content

def test_sanitization():
    html_input = """
    <style>
        .my-class { color: red; }
    </style>
    <div class="my-class" id="my-id" style="font-weight: bold;">Hello</div>
    <script>alert('bad');</script>
    """
    
    sanitized = sanitize_blog_content(html_input, 'html')
    
    print("Original:")
    print(html_input)
    print("\nSanitized:")
    print(sanitized)
    
    # Checks
    if "<style>" in sanitized and ".my-class { color: red; }" in sanitized:
        print("\nSUCCESS: <style> tag preserved.")
    else:
        print("\nFAILURE: <style> tag removed or content missing.")
        return False
        
    if 'class="my-class"' in sanitized or 'class="my-class"' in sanitized: # bleach might reorder attributes
        print("SUCCESS: class attribute preserved.")
    else:
        print("FAILURE: class attribute removed.")
        
    if 'id="my-id"' in sanitized:
        print("SUCCESS: id attribute preserved.")
    else:
        print("FAILURE: id attribute removed.")

    if 'style="font-weight: bold;"' in sanitized: # bleach might normalize style
        print("SUCCESS: style attribute preserved.")
    else:
        print("FAILURE: style attribute removed.")
        
    if "<script>" in sanitized:
        print("FAILURE: <script> tag NOT removed.")
        return False
    else:
        print("SUCCESS: <script> tag removed.")
        
    return True

if __name__ == "__main__":
    if test_sanitization():
        sys.exit(0)
    else:
        sys.exit(1)
