import codecs
import subprocess
import time  # Add this line if it's missing
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import datetime
import vlc
import os

# Path for logs, ensure this directory exists or create it
LOGS_ = '/Users/ahmedhentati/passetonbilletlogs/'

# URL of the page with Taylor Swift tickets
#url = "https://www.passetonbillet.fr/artists/taylor-swift"
url = "https://www.passetonbillet.fr/events/104837"

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1280,800")
options.add_argument('--no-sandbox')

# macOS Notification Function
def show_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])

# Function to check if Taylor Swift tickets are available
from selenium.common.exceptions import NoSuchElementException

def check_tickets_available(now):
    print("Checking for Taylor Swift tickets at " + now)
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    no_tickets_element = None  # Initialize outside the try block
    
    try:
        retries = 3
        for _ in range(retries):
            try:
                no_tickets_element = driver.find_element(By.XPATH, "//p[contains(text(),'Aucun billet disponible')]")
                break  # Element found, exit loop
            except NoSuchElementException:
                print("No tickets element not found. Retrying...")
                time.sleep(2)  # Wait for 2 seconds before retrying
        
        if no_tickets_element is None:
            play_alarm_sound()
            print("Tickets are available!")
            show_notification("Taylor Swift Tickets Available!", "Check PasseTonBillet now!")
        else:
            print("No tickets available at this moment.")
    except Exception as e:
        print("Error checking tickets: ", str(e))
    finally:
        driver.quit()


def main():
    print("Starting to monitor Taylor Swift tickets on PasseTonBillet.")
    print("Press CTRL+C to abort...\n")
    
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            start_time = time.time()  # Start time for measuring duration
            check_tickets_available(now)
            end_time = time.time()  # End time for measuring duration
            duration = end_time - start_time  # Calculate duration of check
        except Exception as e:
            print("Error occurred during check:", str(e))
            duration = 0  # Set default duration in case of error
        time.sleep(60 - duration)  # Adjust sleep duration based on the time taken for check


def play_alarm_sound():
    p = vlc.MediaPlayer("alarm.wav")
    p.play()


if __name__ == '__main__':
    main()
