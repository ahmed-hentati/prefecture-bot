import codecs
import subprocess
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
url = "https://www.passetonbillet.fr/artists/taylor-swift"
#url = "https://www.passetonbillet.fr/artists/patrick-bruel"

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1280,800")
options.add_argument('--no-sandbox')

# macOS Notification Function
def show_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])

# Function to check if Taylor Swift tickets are available
def check_tickets_available(now):
    print("Checking for Taylor Swift tickets at " + now)
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    try:
        wait = WebDriverWait(driver, 10)
        # Assuming tickets are listed in a container with a specific class or ID
        #tickets_available = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".section-all-tickets")))
        #sno_tickets_element = driver.find_element(By.CSS_SELECTOR, ".text-lg.font-semibold.text-center")
        no_tickets_element = driver.find_element_by_xpath("//p[text()='Aucun billet disponible']")


        
        if not no_tickets_element:
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
        check_tickets_available(now)
        sleep(60)  # Check every minute

def play_alarm_sound():
    p = vlc.MediaPlayer("alarm.wav")
    p.play()


if __name__ == '__main__':
    main()
