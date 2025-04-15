import random
import time
import traceback
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Setup Chrome with options to prevent it from closing on error
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)  # Keep browser open when script finishes/crashes

# (Optional) Redirect ChromeDriver logs to /dev/null to hide SSL errors (or "nul" on Windows)
service = Service(log_path="/dev/null")
driver = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(driver, 20)  # Increased wait time to 20 seconds

# Function to safely find and fill a field
def find_and_fill_field(field_identifiers, value, field_name="field"):
    for method, identifier in field_identifiers:
        try:
            print(f"Trying to find {field_name} using {method}: {identifier}")
            if method == "XPATH":
                field = driver.find_element(By.XPATH, identifier)
            elif method == "CSS":
                field = driver.find_element(By.CSS_SELECTOR, identifier)
            elif method == "NAME":
                field = driver.find_element(By.NAME, identifier)
            elif method == "ID":
                field = driver.find_element(By.ID, identifier)
            
            # Try interacting with the field
            field.click()
            time.sleep(0.5)
            field.clear()
            time.sleep(0.5)
            field.send_keys(value)
            print(f"Successfully filled {field_name} with {value}")
            return True
        except Exception as e:
            print(f"Failed with {method}: {identifier}. Error: {str(e)}")
    
    # If all methods failed, try JavaScript as last resort
    try:
        print(f"Trying JavaScript to fill {field_name}")
        if "email" in field_name.lower():
            driver.execute_script(f"document.querySelector('input[type=\"email\"]').value = '{value}';")
        elif "name" in field_name.lower():
            driver.execute_script(f"""
                var inputs = document.querySelectorAll('input');
                for(var i=0; i<inputs.length; i++) {{
                    var input = inputs[i];
                    if(input.type !== 'email' && input.type !== 'password' && 
                       (input.name.toLowerCase().includes('name') || 
                        input.id.toLowerCase().includes('name') ||
                        input.placeholder.toLowerCase().includes('name'))) {{
                        input.value = '{value}';
                        return true;
                    }}
                }}
            """)
        elif "password" in field_name.lower():
            driver.execute_script(f"document.querySelector('input[type=\"password\"]').value = '{value}';")
        
        print(f"JavaScript attempt to fill {field_name} complete")
        return True
    except Exception as e:
        print(f"JavaScript attempt failed: {str(e)}")
        return False

try:
    # STEP 1: Get fake email
    driver.get("https://www.fakemail.net/")
    email_elem = wait.until(EC.presence_of_element_located((By.ID, "email")))
    fake_email = email_elem.text.strip()
    print(f"Got fake email: {fake_email}")

    # STEP 2: Go to Frame.io
    driver.execute_script("window.open('https://accounts.frame.io/signup', '_blank');")
    driver.switch_to.window(driver.window_handles[1])

    # STEP 3: Fill out initial form (email field)
    print("Filling initial email field...")
    # Wait for email field and ensure it's fully loaded
    email_field = wait.until(EC.element_to_be_clickable((By.NAME, "email")))
    email_field.clear()
    email_field.click()
    time.sleep(1)
    email_field.send_keys(fake_email)
    
    # Click the initial "Let's go" button
    print("Clicking initial 'Let's go' button...")
    try:
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='lets-go-button']")))
        button.click()
    except:
        # JavaScript fallback
        driver.execute_script("""
            var buttons = document.querySelectorAll('button[type="submit"]');
            if(buttons.length > 0) buttons[0].click();
        """)

    # STEP 4: Main signup form - Wait longer to ensure page loads
    print("Waiting for main signup form...")
    time.sleep(5)  # Give more time for the page to fully load
    
    # Generate a random number for the name
    random_number = random.randint(100, 999)
    full_name = f"Editor RBCB{random_number}"
    
    # Try multiple ways to find and fill the name field
    name_identifiers = [
        ("NAME", "name"),
        ("NAME", "full_name"),
        ("NAME", "fullName"),
        ("XPATH", "//input[@placeholder='Full name']"),
        ("XPATH", "//input[contains(@placeholder, 'name') or contains(@placeholder, 'Name')]"),
        ("XPATH", "//label[contains(text(), 'Full name')]/following::input[1]"),
        ("XPATH", "//label[contains(text(), 'Name')]/following::input[1]"),
        ("XPATH", "//input[contains(@class, 'name') or contains(@id, 'name')]"),
        ("CSS", "input:not([type='email']):not([type='password'])")
    ]
    name_filled = find_and_fill_field(name_identifiers, full_name, "name field")
    
    # Try multiple ways to find and fill the password field
    password_identifiers = [
        ("NAME", "password"),
        ("XPATH", "//input[@type='password']"),
        ("XPATH", "//input[@placeholder='Password']"),
        ("XPATH", "//label[contains(text(), 'Password')]/following::input[1]"),
        ("CSS", "input[type='password']")
    ]
    password_filled = find_and_fill_field(password_identifiers, "Pejabat!55", "password field")
    
    # See if there are any fields we missed
    if not (name_filled and password_filled):
        print("Some fields couldn't be filled. Trying to find all input fields...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input fields")
        for i, input_field in enumerate(inputs):
            try:
                field_type = input_field.get_attribute("type")
                field_name = input_field.get_attribute("name") or input_field.get_attribute("id") or input_field.get_attribute("placeholder") or "unknown"
                print(f"Input {i+1}: Type={field_type}, Name/ID/Placeholder={field_name}")
            except:
                print(f"Input {i+1}: Could not get attributes")
    
    # Try to submit the form
    print("Attempting to click 'Sign up' button...")
    try:
        # Primary method - wait for and click using data-testid
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='signup-button']")))
        button.click()
        print("Successfully clicked signup button using data-testid")
    except:
        # Fallback method - click using submit type
        print("Trying fallback method")
        driver.execute_script("""
            document.querySelector('button[type="submit"]').click();
        """)
        print("Executed fallback click")
    
    # STEP 5: Add a 3-second delay before switching back to Fakemail.net
    print("Waiting for 3 seconds before switching back to Fakemail.net...")
    time.sleep(3)
    print("Returning to Fakemail.net tab...")
    driver.switch_to.window(driver.window_handles[0])
    print("Looking for email from Frame.io...")

    email_opened = False
    for _ in range(10):  # Retry up to 10 times with a short delay
        try:
            # Locate all rows in the email table
            email_rows = driver.find_elements(By.CSS_SELECTOR, "tr.hidden-xs.hidden-sm.klikaciRadek.newMail")
            # Check each row for matching text
            for row in email_rows:
                row_text = row.text.lower()
                if "frame.io" in row_text and "new security code" in row_text:
                    print("Email from Frame.io with 'New Security Code' found.")
                    row.click()  # Click the email row
                    email_opened = True
                    break
            if email_opened:
                break
            else:
                print("Email not found yet. Retrying in 5 seconds...")
                time.sleep(5)
        except Exception as e:
            print(f"Error while checking emails: {str(e)}")
            time.sleep(5)

    if not email_opened:
        raise Exception("Email from Frame.io not found within the retry limit.")

    # STEP 6: Click Confirm Email button
    print("Attempting to click 'Confirm Email' button...")
    # 6a) Wait for the iframe that contains the email body
    try:
        email_iframe = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "iframe#iframeMail, iframe.emailFrame"
        )))
        driver.switch_to.frame(email_iframe)
        print("✅ Switched into email iframe")
    except TimeoutException:
        print("❌ Timeout: email iframe not found")
        raise

    # 6b) Inside the iframe, try to click the link by text first
    try:
        confirm_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Confirm Email"))
        )
        confirm_link.click()
        print("✅ Clicked 'Confirm Email' via LINK_TEXT")
    except TimeoutException:
        print("❌ Link not found by LINK_TEXT, trying CSS selector...")
        # Try CSS selector
        try:
            confirm_link = wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "td[bgcolor='#5b53ff'] a[href*='confirm-email-link']"
                ))
            )
            confirm_link.click()
            print("✅ Clicked 'Confirm Email' via CSS selector")
        except TimeoutException:
            print("❌ Link not found by CSS selector, trying JavaScript fallback...")
            # JavaScript fallback
            try:
                clicked = driver.execute_script("""
                    const link = document.querySelector("td[bgcolor='#5b53ff'] a[href*='confirm-email-link']");
                    if (link) { link.click(); return true; }
                    return false;
                """)
                if clicked:
                    print("✅ Clicked 'Confirm Email' via JavaScript")
                else:
                    print("❌ 'Confirm Email' link not found via JavaScript")
            except Exception as e:
                print(f"❌ JS fallback failed: {e}")

    # 6c) Switch back to the main document so further steps (if any) work
    driver.switch_to.default_content()
    print("✅ Switched back to main document")

    # STEP 7: Click Continue button
    print("Attempting to click 'Continue' button...")
    try:
        # Adjust the selector as needed if the element is not a button
        continue_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.flex-x9ump0-0.Button__ChildrenWrapper-tzx5l-1.cbDFCh"))
        )
        continue_button.click()
        print("✅ Clicked 'Continue' button")
    except TimeoutException:
        print("❌ Timeout: 'Continue' button not found via CSS selector, trying JS fallback...")
        try:
            clicked = driver.execute_script("""
                const btns = Array.from(document.querySelectorAll('div'));
                const btn = btns.find(el => el.className.includes('Button__ChildrenWrapper') && el.textContent.trim() === 'Continue');
                if (btn) { btn.click(); return true; }
                return false;
            """)
            if clicked:
                print("✅ Clicked 'Continue' button via JavaScript fallback")
            else:
                print("❌ 'Continue' button not found via JavaScript fallback")
        except Exception as e:
            print(f"❌ JS fallback for 'Continue' button failed: {e}")

    print("\n✅ Email confirmation process completed successfully.")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
    print("Stack trace:")
    traceback.print_exc()
    print("\nBrowser will remain open for debugging.")

# Don't close the driver - the detach option will keep it open
