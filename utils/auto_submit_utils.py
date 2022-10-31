import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

error = 'ERROR: '
GLOBAL_WAIT_TIME: int = 15
SUBMISSION_WAIT_TIME: int = 600

def start_selenium(creds, url, model_name, iam_role=True):
    good = True
    retry_count = 0

    # Start Selenium webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    wait = WebDriverWait(driver, GLOBAL_WAIT_TIME)
    pending = WebDriverWait(driver, SUBMISSION_WAIT_TIME)
    driver.maximize_window()

    def login(creds, iam_role=True):
        print(time.ctime() + ' | Logging in..')

        if not iam_role:
            driver.get('https://console.aws.amazon.com')
            time.sleep(2)
            elem_username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
            elem_username.clear()
            elem_username.send_keys(creds[0])
            elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='next_button']")))
            elem_submit.click()

            check_captcha()

            elem_password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='password']")))
            elem_password.clear()
            elem_password.send_keys(creds[1])

            elem_submit = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='signin_button']")))
            elem_submit.click()

        else:
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

    def check_captcha():
        # Checks if there is a captcha so a human can enter the letters
        # TODO: Create an AI that can read the captcha and enter the letters automatically lol
        print('Looking for CAPTHCA prompt...')
        try:
            time.sleep(2)
            captcha_image = driver.find_element(By.XPATH, "//img[@id='captcha_image']")
        except NoSuchElementException:
            print("No CAPTCHA found.")
        else:
            input('CAPTCHA found. Please complete the CAPTCHA. Then press ENTER to continue...')


    # Log in
    try:
        login(creds, iam_role=iam_role)
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
                choose_model = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '%s')]/ancestor::li" %model_name)))
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

