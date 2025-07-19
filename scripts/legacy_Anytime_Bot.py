"""
Legacy Anytime Bot - Selenium Implementation Reference

This file provides reference implementation of ClubOS messaging using Selenium
for comparison with the pure API approach. This shows how the web interface
works, which helps us understand what the API needs to replicate.

NOTE: This is for reference only - the goal is to replace Selenium with pure API calls.
"""

import time
import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class AnytimeBotSelenium:
    """
    Legacy Selenium-based ClubOS bot for reference.
    
    This implementation works but we want to replace it with pure API calls.
    It's included here to understand the exact web interface workflow.
    """
    
    def __init__(self, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.logged_in = False
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
                
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("WebDriver setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to ClubOS using Selenium.
        
        This shows the exact steps that work in the web interface.
        """
        try:
            logger.info("Navigating to login page...")
            self.driver.get("https://anytime.club-os.com/action/Authentication/log-in")
            
            # Wait for login form
            wait = WebDriverWait(self.driver, 30)
            
            # Find username field
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            # Find password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit login form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect to dashboard
            wait.until(lambda driver: "dashboard" in driver.current_url.lower())
            
            self.logged_in = True
            logger.info("Login successful!")
            
            # Capture session data for API reference
            self._capture_session_data()
            
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def send_message(self, member_id: str, message_type: str, content: str, subject: str = None) -> bool:
        """
        Send message using Selenium web interface.
        
        This demonstrates the exact workflow that we need to replicate with API calls.
        """
        if not self.logged_in:
            logger.error("Not logged in")
            return False
            
        try:
            # Navigate to member profile
            member_url = f"https://anytime.club-os.com/action/Dashboard/member/{member_id}"
            logger.info(f"Navigating to member profile: {member_url}")
            self.driver.get(member_url)
            
            wait = WebDriverWait(self.driver, 30)
            
            # Wait for page to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Look for messaging section/form
            # Note: Exact selectors depend on ClubOS interface structure
            
            if message_type.lower() == "sms":
                return self._send_sms_message(content, wait)
            elif message_type.lower() == "email":
                return self._send_email_message(content, subject, wait)
            else:
                logger.error(f"Unsupported message type: {message_type}")
                return False
                
        except Exception as e:
            logger.error(f"Message sending failed: {str(e)}")
            return False
    
    def _send_sms_message(self, content: str, wait: WebDriverWait) -> bool:
        """Send SMS message through web interface"""
        try:
            # Look for SMS option/button
            sms_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'SMS') or contains(text(), 'Text')]"))
            )
            sms_button.click()
            
            # Find message input field
            message_field = wait.until(
                EC.presence_of_element_located((By.NAME, "message"))
            )
            message_field.clear()
            message_field.send_keys(content)
            
            # Submit message
            send_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
            send_button.click()
            
            # Wait for confirmation
            time.sleep(2)
            
            # Check for success indicator
            success = self._check_message_success()
            
            if success:
                logger.info("SMS sent successfully via Selenium!")
            else:
                logger.error("SMS sending may have failed")
                
            return success
            
        except Exception as e:
            logger.error(f"SMS sending error: {str(e)}")
            return False
    
    def _send_email_message(self, content: str, subject: str, wait: WebDriverWait) -> bool:
        """Send Email message through web interface"""
        try:
            # Look for Email option/button
            email_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Email') or contains(text(), 'Mail')]"))
            )
            email_button.click()
            
            # Find subject field if available
            if subject:
                try:
                    subject_field = self.driver.find_element(By.NAME, "subject")
                    subject_field.clear()
                    subject_field.send_keys(subject)
                except NoSuchElementException:
                    logger.warning("Subject field not found, continuing without")
            
            # Find message input field
            message_field = wait.until(
                EC.presence_of_element_located((By.NAME, "message"))
            )
            message_field.clear()
            message_field.send_keys(content)
            
            # Submit message
            send_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
            send_button.click()
            
            # Wait for confirmation
            time.sleep(2)
            
            # Check for success indicator
            success = self._check_message_success()
            
            if success:
                logger.info("Email sent successfully via Selenium!")
            else:
                logger.error("Email sending may have failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            return False
    
    def _check_message_success(self) -> bool:
        """Check if message was sent successfully"""
        try:
            # Look for success indicators in the page
            success_indicators = [
                "message sent",
                "sent successfully", 
                "success",
                "delivered"
            ]
            
            page_text = self.driver.page_source.lower()
            
            for indicator in success_indicators:
                if indicator in page_text:
                    return True
            
            # Check for error indicators
            error_indicators = [
                "error",
                "failed",
                "something isn't right",
                "unable to send"
            ]
            
            for error in error_indicators:
                if error in page_text:
                    logger.error(f"Found error indicator: {error}")
                    return False
            
            # If no clear indicator, assume success (may need refinement)
            return True
            
        except Exception as e:
            logger.error(f"Error checking message success: {str(e)}")
            return False
    
    def _capture_session_data(self):
        """
        Capture session data for API reference.
        
        This helps understand what authentication data is available
        in a working Selenium session.
        """
        try:
            # Capture cookies
            cookies = self.driver.get_cookies()
            logger.info(f"Session cookies: {len(cookies)} cookies found")
            
            for cookie in cookies:
                if 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                    logger.info(f"Auth cookie: {cookie['name']} = {cookie['value'][:20]}...")
            
            # Capture current URL and page source for analysis
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # Look for CSRF tokens in page source
            page_source = self.driver.page_source
            if 'csrf' in page_source.lower():
                logger.info("CSRF tokens found in page source")
            
            # Look for API configuration in JavaScript
            if 'api' in page_source.lower():
                logger.info("API configuration found in page source")
            
        except Exception as e:
            logger.error(f"Error capturing session data: {str(e)}")
    
    def get_member_profile_data(self, member_id: str) -> Dict[str, Any]:
        """
        Get member profile data for reference.
        
        This shows what data is available on the member profile page
        that might be needed for API calls.
        """
        try:
            member_url = f"https://anytime.club-os.com/action/Dashboard/member/{member_id}"
            self.driver.get(member_url)
            
            wait = WebDriverWait(self.driver, 30)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            profile_data = {
                'url': member_url,
                'title': self.driver.title,
                'cookies': self.driver.get_cookies(),
                'page_source_length': len(self.driver.page_source)
            }
            
            # Look for hidden form fields
            hidden_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='hidden']")
            profile_data['hidden_fields'] = {}
            
            for input_field in hidden_inputs:
                name = input_field.get_attribute('name')
                value = input_field.get_attribute('value')
                if name:
                    profile_data['hidden_fields'][name] = value
            
            logger.info(f"Profile data captured: {len(profile_data['hidden_fields'])} hidden fields")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error getting profile data: {str(e)}")
            return {}
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")

def demo_selenium_workflow():
    """
    Demonstrate the working Selenium workflow for reference.
    
    This shows exactly how the web interface works, which helps
    understand what the API implementation needs to replicate.
    """
    import os
    
    username = os.getenv('CLUBOS_USERNAME', 'your_username')
    password = os.getenv('CLUBOS_PASSWORD', 'your_password')
    member_id = os.getenv('CLUBOS_MEMBER_ID', '187032782')
    
    if username == 'your_username' or password == 'your_password':
        logger.warning("Please set CLUBOS_USERNAME and CLUBOS_PASSWORD environment variables")
        return
    
    bot = AnytimeBotSelenium(headless=True)
    
    try:
        logger.info("=== Selenium Workflow Demo ===")
        
        # Setup WebDriver
        if not bot.setup_driver():
            logger.error("Failed to setup WebDriver")
            return
        
        # Login
        logger.info("Step 1: Login")
        if not bot.login(username, password):
            logger.error("Login failed")
            return
        
        # Get member profile data
        logger.info("Step 2: Get member profile data")
        profile_data = bot.get_member_profile_data(member_id)
        logger.info(f"Profile data: {profile_data}")
        
        # Send test SMS
        logger.info("Step 3: Send SMS message")
        sms_success = bot.send_message(
            member_id=member_id,
            message_type="sms",
            content="Test SMS from Selenium bot - please ignore"
        )
        logger.info(f"SMS result: {'SUCCESS' if sms_success else 'FAILED'}")
        
        # Send test Email
        logger.info("Step 4: Send Email message")
        email_success = bot.send_message(
            member_id=member_id,
            message_type="email", 
            content="Test email from Selenium bot - please ignore",
            subject="Test Email Subject"
        )
        logger.info(f"Email result: {'SUCCESS' if email_success else 'FAILED'}")
        
        logger.info("=== Selenium Demo Complete ===")
        logger.info(f"SMS: {'✅' if sms_success else '❌'}")
        logger.info(f"Email: {'✅' if email_success else '❌'}")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
    
    finally:
        bot.close()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Note: This requires ChromeDriver to be installed
    logger.info("This is a reference implementation using Selenium")
    logger.info("The goal is to replace this with pure API calls")
    logger.info("Use this to understand the web interface workflow")
    
    # Uncomment to run demo (requires ChromeDriver)
    # demo_selenium_workflow()