import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import datetime
import vlc
import requests

# URL of the Paris 2024 basketball page
url = "https://tickets.paris2024.org/events/jeux-olympiques-225/basketball-2236/?affiliate=24R&venueNames=Arena+Bercy"

# Telegram Bot credentials
TELEGRAM_BOT_TOKEN = "7186667477:AAGtxMMcP8EJbqz495qnWJabXQQMNk4u6r4"  # Replace with your bot token
TELEGRAM_CHAT_ID = "6092046595"  # Replace with your chat ID

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1280,800")
options.add_argument('--no-sandbox')

# macOS Notification Function
def show_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])

# Telegram Notification Function
def send_telegram_notification(title, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{title}\n\n{message}"
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("Failed to send Telegram notification:", response.text)

def check_tickets_available(now):
    print("Checking for Basketball tickets at " + now)
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        driver.execute_script("window.scrollBy(0, 200);")
        
        # Adding a sleep here to keep the browser open for a while
        time.sleep(5)  # Wait 5 seconds for the page to load

        # Locate all listing items
        tickets = driver.find_elements(By.XPATH, "//article[@class='listing listing-container u-shadow clearfix standard-gray-shadow theme-element-border theme-content-bg theme-element-radius']")
        for ticket in tickets:
            try:
                # Ensure we are targeting female basketball tickets by checking for the female icon
                gender_icons = ticket.find_elements(By.XPATH, ".//i[@class='icon theme-text-color icon-gender-female']")
                if len(gender_icons) > 0:  # Only proceed if the ticket is for a female event
                    
                    # Extract relevant ticket information
                    title = ticket.find_element(By.XPATH, ".//div[@class='event-listing-city theme-text-color']").text
                    price_text = ticket.find_element(By.XPATH, ".//div[@class='listing-event-status theme-text-highlight-color theme-interaction-color hidden-xs hidden-sm listing-event-price']").text
                    price = float(price_text.replace('À partir de ', '').replace('€', '').replace(',', '').strip())
                    
                    # Set your own criteria for which tickets to notify
                    if "Basketball" in title and price < 200:  # Adjust price threshold as needed
                        play_alarm_sound()
                        print(f"Tickets available: {title} for {price_text}!")
                        show_notification("Basketball Tickets Available!", f"{title} for {price_text} on Paris 2024!")
                        send_telegram_notification("Basketball Tickets Available!", f"{title} for {price_text} on Paris 2024!")
                        break
            except (NoSuchElementException, ValueError) as e:
                print("Skipping a ticket due to error: ", str(e))
        else:
            print("No suitable tickets available at this moment.")
    except Exception as e:
        print("Error checking tickets: ", str(e))
    #finally:
        # Add an input prompt to keep the browser open until you're done
     #   input("Press Enter to close the browser...")
      #  driver.quit()

def main():
    print("Starting to monitor Basketball tickets on Paris 2024.")
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
