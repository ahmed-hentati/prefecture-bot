import codecs
import subprocess
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
import datetime
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import os
import vlc
import random

# Update LOGS_ path for macOS, ensure this directory exists or create it
LOGS_ = '/Users/YourUsername/PrefectureLogs/'

# Dictionary for prefecture desks
PrefectDesks = {
    'planning13782': 'planning1', 
    'planning20779': 'planning2', 
    'planning21505': 'planning3'
}

# Options to run Chrome
options = webdriver.ChromeOptions()

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

# Update with your prefecture URL
url = "https://www.val-doise.gouv.fr/booking/create/11343/1"

# Sentences indicating no available appointment spots
NoAppointmentAvailable_Sentences = [
    "existe plus de plage horaire libre pour votre demande",
    "de rendez-vous disponibles pour le moment",
    "The server returned an invalid or incomplete response"
]

Error_403 = ["403", "Request forbidden by administrative rules", "Service surchargé", "Aucun accès à Internet"]

Rdv_filename = os.path.join(LOGS_, 'rdvs_status.txt')
Error_filename = os.path.join(LOGS_, 'log_errors.txt')

options.add_argument("--window-size=1280,800")
options.add_argument('--no-sandbox')

# macOS Notification Function
def show_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])

def check_available_spot(now):
    print("Checking for appointment " + now)

    desk_key = random.choice(list(PrefectDesks.keys()))
    print("Random desk key " + desk_key)

    desk_value = PrefectDesks[desk_key]
    print("Corresponds to desk value " + desk_value)

    user_agent = user_agent_rotator.get_random_user_agent()
    options.add_experimental_option("detach", True)
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 5)
    wait.until(ec.element_to_be_clickable((By.ID, desk_key)))
    driver.find_element(By.ID, desk_key).click()

    next_button = wait.until(ec.element_to_be_clickable((By.NAME, 'nextButton')))
    driver.execute_script("return arguments[0].scrollIntoView(true);", next_button)
    sleep(1)
    next_button.click()

    take_screenshot(driver, now)
    save_source(driver, now)

    if any(x in driver.page_source for x in NoAppointmentAvailable_Sentences):
        places_are_already_taken = True
        driver.quit()
    else:
        places_are_already_taken = False
        play_alarm_sound()
        display(desk_value, now)

    return places_are_already_taken, desk_value, desk_key

def take_screenshot(driver, now):
    save_captures_path = os.path.join(LOGS_, "captures")
    file_name = f'capture {now}.png'
    complete_capture_name = os.path.join(save_captures_path, file_name)
    driver.get_screenshot_as_file(complete_capture_name)

def display(desk_value, now):
    show_notification('New spot is available ' + now, str(desk_value))

def write_results(places_are_already_taken, desk_value, now):
    with open(Rdv_filename, 'a') as f:
        if places_are_already_taken:
            f.write(f'{now} No place is available! Desk Tested {desk_value}\n')
        else:
            f.write(f'{now} At least one place is available! Desk {desk_value}\n')

def play_alarm_sound():
    p = vlc.MediaPlayer("alarm.wav")
    p.play()

def save_source(driver, now):
    file_name = f'source {now}.html'
    save_sources_path = os.path.join(LOGS_, "sources")
    complete_source_name = os.path.join(save_sources_path, file_name)
    f = codecs.open(complete_source_name, "w", "utf-8")
    h = driver.page_source
    f.write(h)

def log_error(e, now):
    with open(Error_filename, 'a') as f:
        f.write(f'{now} Error {e}\n')

def main():
    print(r"""
    ____            ____          __                     ____        __ 
   / __ \________  / __/__  _____/ /___  __________     / __ )____  / /_
  / /_/ / ___/ _ \/ /_/ _ \/ ___/ __/ / / / ___/ _ \   / __  / __ \/ __/
 / ____/ /  /  __/ __/  __/ /__/ /_/ /_/ / /  /  __/  / /_/ / /_/ / /_  
/_/   /_/   \___/_/  \___/\___/\__/\__,_/_/   \___/  /_____/\____/\__/  
    """)
    print('Starting to monitor the reservation system.')
    print('Press CTRL+C to abort...\n')
    attempts = 0
    while True:
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
            places_are_already_taken, desk_value, desk_key = check_available_spot(now)
        except Exception as e:
            log_error(repr(e), str(now))
            print('Last check failed           ' + now)
        else:
            write_results(places_are_already_taken, desk_value, now)
            print('Last Desk checked ' + desk_value + ' ' + now)
        finally:
            attempts += 1
            print('Attempt number : ' + str(attempts))
            sleep(40)

if __name__ == '__main__':
    main()
