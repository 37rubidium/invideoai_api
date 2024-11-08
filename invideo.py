#
# Will login to invideo and download video
#

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import os
import base64
import re
import google.auth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define your scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

username = "craigsimmons991@gmail.com"

gecko_path = '/snap/bin/firefox.geckodriver'  
service = Service(gecko_path)
# Specify your desired download path
download_path = "/home/salman/workspace/kraftbot/content"
options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", download_path)

driver = webdriver.Firefox(service=service, options=options)

# Open the specified URL
url = "https://ai.invideo.io/login"

def authenticate_gmail():
    creds = None
    # Check if the token.json file exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials are available, go through OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google.auth.oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_login_code():
    # Authenticate and initialize the API service
    # Initialize the Firefox WebDriver
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    # Get the user's messages
    results = service.users().messages().list(userId='me', q='subject:login code').execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return None

    # Get the latest message
    message = service.users().messages().get(userId='me', id=messages[0]['id']).execute()

    # Decode the message content
    for part in message['payload']['parts']:
        if part['mimeType'] == 'text/plain':
            data = part['body']['data']
            decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')

            # Extract code using regex (assuming a 6-digit code format)
            match = re.search(r'\b\d{6}\b', decoded_data)
            if match:
                return match.group(0)

    print("No login code found in the latest email.")
    return None


def login():
    # Open invideo login
    driver.get(url)
    time.sleep(5)

    # Find email field and enter email
    driver.find_element("name", "email_id").send_keys(username)
    driver.find_element("name", "email_id").send_keys(Keys.ENTER)
    time.sleep(3)

    # Retrieve login code from Gmail
    login_code = get_login_code()

    # Find code field and enter email
    driver.find_element("name", "code").send_keys(login_code)
    driver.find_element("name", "code").send_keys(Keys.ENTER)

    # Wait for a few seconds to see the opened page
    time.sleep(5)

def create_video(vid_url):
    driver.get(vid_url)
    time.sleep(2)
    try:
        # Wait for the button to be visible (or present) on the page
        download_button = WebDriverWait(driver, 600).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'c-eZwudA')]"))
        )
        # If the button exists, click it
        download_button.click()
     
    except Exception as e:
        print("Timeout waiting for video creation", e)

    # Choose stock watermarks (removed after premium upgrade)
    # stockwm_btn = driver.find_element(By.XPATH, "//p[contains(@class, 'fkRdRB') and text()='Stock watermarks']")
    # stockwm_btn.click()
    # # Choose normal ai branding (removed after premium upgrade)
    # branding_btn = driver.find_element(By.XPATH, "//p[contains(@class, 'fkRdRB') and text()='Normal']")
    # branding_btn.click()


    # Press continue button to download
    continue_btn = driver.find_element(By.XPATH, "//p[contains(@class, 'fkRdRB') and text()='Continue']")
    continue_btn.click()

    # wait for page to load and download to complete
    time.sleep(180)
    driver.quit()