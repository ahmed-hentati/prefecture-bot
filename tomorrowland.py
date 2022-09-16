import codecs
import subprocess
import time  # Add this line if it's missing
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import datetime
import vlc
import os

# Path for logs, ensure this directory exists or create it
LOGS_ = '/Users/ahmedhentati/passetonbilletlogs/'

# URL of the Viagogo page with the listings
url = "https://www.viagogo.com/Festival-Tickets/International-Festivals/Tomorrowland-Festival-Tickets/E-152848445?quantity=1&sortDirection=0&sortBy=NEWPRICE&estimatedFees=true"

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1280,800")
options.add_argument('--no-sandbox')

# macOS Notification Function
def show_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])

def check_tickets_available(now):
    print("Checking for Tomorrowland tickets at " + now)
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    driver.execute_script("window.scrollBy(0, 200);")

    try:
        tickets = driver.find_elements(By.XPATH, "//div[@data-index]")
        for ticket in tickets:
            try:
                title = ticket.find_element(By.XPATH, ".//div[contains(@class, 'sc-hlalgf-0 sc-hlalgf-2')]").text
                price_text = ticket.find_element(By.XPATH, ".//div[contains(@class, 'sc-hlalgf-0') and contains(text(), '€')]").text
                price = float(price_text.replace('€', '').replace(',', ''))

                if "Magnificent Greens" in title and price < 730:
                    play_alarm_sound()
                    print(f"Tickets available: {title} for {price_text}!")
                    show_notification("Tomorrowland Tickets Available!", f"{title} for {price_text} on Viagogo!")
                    break
            except (NoSuchElementException, ValueError) as e:
                print("Skipping a ticket due to error: ", str(e))
        else:
            print("No suitable tickets available at this moment.")
    except Exception as e:
        print("Error checking tickets: ", str(e))
    finally:
        time.sleep(15)
        driver.quit()

def main():
    print("Starting to monitor Tomorrowland tickets on Viagogo.")
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
        sleep_time = max(60 - duration, 0)  # Ensure sleep time is non-negative
        time.sleep(sleep_time)  # Adjust sleep duration based on the time taken for check

def play_alarm_sound():
    p = vlc.MediaPlayer("alarm.wav")
    p.play()

if __name__ == '__main__':
    main()
