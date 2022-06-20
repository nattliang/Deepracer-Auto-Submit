import time
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def start_selenium(creds, url, model_name):
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
        driver.get('https://%s.signin.aws.amazon.com/console' %creds[0])
        time.sleep(2)
        elem_username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='username']")))
        elem_username.clear()
        elem_username.send_keys(creds[1])

        elem_password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='password']")))
        elem_password.clear()
        elem_password.send_keys(creds[2])

        elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='input_signin_button']/a")))
        elem_submit.click() 

    # Log in as IAM user
    try:
        login(creds)
    except:
        print(error + 'Login Failed. Check credentials.')
        good = False

    # Go to race url
    if good:
        try:
            time.sleep(5)
            driver.get(url)
            time.sleep(5)
            race = pending.until(EC.presence_of_element_located((By.XPATH, "//button[@data-analytics='league_leaderboard_race_again']")))
        except Exception:
            print(error + 'Failed finding "Race again" button. Check the url.')
            good = False

    while good:
        while True:
            # Wait for previous submission to finish
            try:
                race_again = pending.until(EC.presence_of_element_located((By.XPATH, "//button[@data-analytics='league_leaderboard_race_again']")))
                driver.execute_script("arguments[0].scrollIntoView(false);", race_again)
                race_again.click()
            except TimeoutException:
                print(error + 'Submission Timeout Reached')
                break
            
            # Choose model and submit it
            try:
                dropdown = wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(), 'Choose a model')]")))
                dropdown.click()
                choose_model = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@title='%s']" %model_name)))
                choose_model.click()
            except Exception:
                print(error + 'Failed to select model with name "%s"' %model_name)
                break

            # Click the submit buttom
            try:
                enter_race = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-analytics='submit_to_leaderboard_accept']")))
                enter_race.click()

                # Check to see if model submitted successfully
                time.sleep(2)
                check_eval = wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(), 'Under evaluation')]")))
                check_eval = check_eval.text
                if check_eval != 'Under evaluation':
                    print(error + 'Model Submission Failed')
                    break
            except Exception:
                print(error + 'Model Submission Failed')
                break
            
        # Retry if failed
        retry_count += 1

        # Break if failed too many attempts
        if retry_count == 20:
            print(time.ctime() + ' | Failed %s time(s). Stopping.' %retry_count)
            driver.quit()
            break

        try:
            driver.get(url)
        except:
            driver.quit()
            break

        # Log back in if logged out
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='input_signin_button']/a")))
            print(time.ctime() + ' | Logged out. Attempting to login again..')

            try:
                login(creds)
            except Exception:
                print(time.ctime() + ' | ERROR: Login Failed')
                driver.quit()
                break

        except Exception:
            print(time.ctime() + ' | Failed %s time(s). Retrying..' %retry_count)


##### FIELDS TO FILL OUT #####
account_id = '' # Your IAM role account ID (12 digit number)
username = '' # Your IAM role username
password = '' # Your IAM role password
race_url = 'https://console.aws.amazon.com/deepracer/home?region=us-east-1#league/arn%3Aaws%3Adeepracer%3A%3A%3Aleaderboard%2F3f4f0e17-37eb-4363-bb9a-3bf1eafdc96b' # The url of the race (default is October Pro Qualifier)
model_to_submit = '' # Name of the model you want to submit
##############################


creds = [account_id, username, password]
if __name__ == '__main__':
    start_selenium(creds, race_url, model_to_submit)