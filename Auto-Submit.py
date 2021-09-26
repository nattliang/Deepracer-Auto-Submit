import time
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def start_selenium(creds, url, model_name):
    good = True
    GLOBAL_WAIT_TIME: int = 30
    SUBMISSION_WAIT_TIME: int = 600

    # Start selenium webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    wait = WebDriverWait(driver, GLOBAL_WAIT_TIME)
    pending = WebDriverWait(driver, SUBMISSION_WAIT_TIME)
    driver.get('https://%s.signin.aws.amazon.com/console' %creds[0])
    driver.maximize_window()

    # Log in as IAM user
    try:
        time.sleep(2)
        elem_username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='username']")))
        elem_username.clear()
        elem_username.send_keys(creds[1])

        elem_password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='password']")))
        elem_password.clear()
        elem_password.send_keys(creds[2])

        elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='input_signin_button']/a")))
        elem_submit.click() 
    except:
        print('ERROR: Login Failed')
        good = False

    # Go to race url
    if good:
        try:
            time.sleep(2)
            driver.get(url)
            time.sleep(5)
            race = pending.until(EC.presence_of_element_located((By.XPATH, "//awsui-button[@data-analytics='league_leaderboard_race_again']")))
        except:
            print('ERROR: Failed finding "Race again" button. Check the url')
            good = False

    while good:
        try:
            race = pending.until(EC.presence_of_element_located((By.XPATH, "//awsui-button[@data-analytics='league_leaderboard_race_again']")))
            race.click()
        except:
            print('ERROR: Submission Timeout Reached')
            break
        
        # Choose model and submit it
        try:
            dropdown = wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='awsui-dropdown-trigger awsui-select-trigger awsui-select-trigger-no-option awsui-select-trigger-variant-label']")))
            dropdown.click()
            choose_model = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@title='%s']" %model_name)))
            choose_model.click()
            enter_race = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='awsui-button awsui-button-variant-primary awsui-hover-child-icons']")))
            enter_race.click()
        except:
            print('ERROR: Model Submission Failed')
            break

##### FIELDS TO FILL OUT #####
account_id = '' # Your IAM role account ID (12 digit number)
username = '' # Your IAM role username
password = '' # Your IAM role password
race_url = 'https://console.aws.amazon.com/deepracer/home?region=us-east-1#league/arn%3Aaws%3Adeepracer%3A%3A%3Aleaderboard%2F9f2d829b-888d-4fc1-ba83-215ce4c01851' # The url of the race (default is September Pro Qualifier)
model_to_submit = '' # Name of the model you want to submit
##############################


creds = [account_id, username, password]
start_selenium(creds, race_url, model_to_submit)