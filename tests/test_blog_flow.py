import requests
import re
import sys

BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
ADMIN_BLOG_NEW_URL = f"{BASE_URL}/admin/blog/new"
BLOG_LIST_URL = f"{BASE_URL}/blog/"

EMAIL = "super@admin.com"
PASSWORD = "1234qa"

def get_csrf_token(html):
    match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

def run_test():
    session = requests.Session()
    
    # 1. Login
    print("1. Accessing Login Page...")
    response = session.get(LOGIN_URL)
    csrf_token = get_csrf_token(response.text)
    if not csrf_token:
        print("Failed to get CSRF token from login page")
        return False
        
    print("2. Logging in...")
    login_data = {
        "email": EMAIL,
        "password": PASSWORD,
        "csrf_token": csrf_token
    }
    response = session.post(LOGIN_URL, data=login_data)
    if "Logout" not in response.text and response.url != f"{BASE_URL}/":
        print("Login failed")
        # print(response.text)
        return False
    print("Login successful")

    # 2. Create Blog Post
    print("3. Accessing Create Blog Post Page...")
    response = session.get(ADMIN_BLOG_NEW_URL)
    csrf_token = get_csrf_token(response.text)
    if not csrf_token:
        print("Failed to get CSRF token from create post page")
        return False
        
    print("4. Creating new blog post...")
    post_title = "Automated Test Post"
    post_content = "This is a test post created by the automated test script."
    post_data = {
        "title": post_title,
        "content": post_content,
        "content_type": "html",
        "status": "published",
        "csrf_token": csrf_token
    }
    
    response = session.post(ADMIN_BLOG_NEW_URL, data=post_data)
    if response.status_code != 200:
        print(f"Failed to create post. Status code: {response.status_code}")
        return False
    
    # Check if we were redirected to dashboard (usually indicates success) or if success message is present
    if "created successfully" in response.text or "dashboard" in response.url:
        print("Blog post creation request completed.")
    else:
        print("Blog post creation might have failed.")
        # print(response.text)

    # 3. Verify on Public Page
    print("5. Verifying on Public Blog Page...")
    response = session.get(BLOG_LIST_URL)
    if post_title in response.text:
        print(f"SUCCESS: '{post_title}' found on public blog page.")
        return True
    else:
        print(f"FAILURE: '{post_title}' NOT found on public blog page.")
        return False

if __name__ == "__main__":
    if run_test():
        sys.exit(0)
    else:
        sys.exit(1)
