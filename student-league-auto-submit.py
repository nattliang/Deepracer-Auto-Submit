import time
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys


def start_selenium(creds, arn, model_name):
    good = True
    retry_count = 0
    error = 'ERROR: '
    GLOBAL_WAIT_TIME: int = 15
    SUBMISSION_WAIT_TIME: int = 600

    # Start Selenium webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    wait = WebDriverWait(driver, GLOBAL_WAIT_TIME)
    pending = WebDriverWait(driver, SUBMISSION_WAIT_TIME)
    driver.maximize_window()

    def login(creds):
        print(time.ctime() + ' | Logging in..')
        driver.get('https://student.deepracer.com')
        time.sleep(2)
        elem_username = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='SignInEmailField']/input")))
        elem_username.clear()
        elem_username.send_keys(creds[0])

        elem_password = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='SignInPwField']/input")))
        elem_password.clear()
        elem_password.send_keys(creds[1])

        elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='SignInBtn']")))
        elem_submit.click() 

    # Log in as IAM user
    try:
        login(creds)
    except Exception:
        print(error + 'Login Failed. Check credentials.')
        good = False

    # Go to race url
    if good:
        try:
            time.sleep(5)
            driver.get('https://student.deepracer.com/leaderboard/' + arn)
            time.sleep(5)
            race = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Race again')]")))
        except Exception:
            print(error + 'Failed finding "Race again" button. Check the url.')
            good = False

    while good:
        while True:
            # Wait for previous submission to finish
            try:
                race_done = pending.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Watch video')]")))
            except TimeoutException:
                print(error + 'Submission Timeout Reached')
                break
            
            # Choose model and submit it
            try:
                driver.get('https://student.deepracer.com/leaderboard/enterRace/' + arn)
                dropdown = wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='']/button[@type='button']")))
                dropdown.click()
                choose_model = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@title='%s']" %model_name)))
                choose_model.click()
            except Exception:
                print(error + 'Failed to select model with name "%s"' %model_name)
                break

            # Click the submit buttom
            try:
                enter_race = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']/span[contains(text(),'Enter race')]")))
                enter_race.click()

                # Check to see if model submitted successfully
                time.sleep(2)
                check_eval = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Race again')]")))

            except Exception:
                print(error + 'Model Submission Failed')
                break
            
        # Retry if failed
        retry_count += 1

        # Break if failed too many attempts
        if retry_count == 10:
            print(time.ctime() + ' | Failed %s time(s). Stopping.' %retry_count)
            driver.quit()
            break

        try:
            driver.get('https://student.deepracer.com/leaderboard/' + arn)
        except Exception:
            driver.quit()
            break

        print(time.ctime() + ' | Failed %s time(s). Retrying..' %retry_count)


##### FIELDS TO FILL OUT #####
email = '' # Your email address
password = '' # Your password
model_to_submit = '' # Name of the model you want to submit
url = 'https://student.deepracer.com/leaderboard/arn%3Aaws%3Adeepracer%3A%3A%3Aleaderboard%2Faf9f936c-b765-4d3a-a59d-99e192f2be42' # The url of the race
##############################


creds = [email, password]
arn = url.split('/')[-1]
start_selenium(creds, arn, model_to_submit)