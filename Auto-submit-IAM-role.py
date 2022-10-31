##### FIELDS TO FILL OUT #####
account_id = '' # Your IAM role account ID (12 digit number)
username = '' # Your IAM role username
password = '' # Your IAM role password
race_url = 'https://us-east-1.console.aws.amazon.com/deepracer/home?region=us-east-1#league/arn%3Aaws%3Adeepracer%3A%3A%3Aleaderboard%2Fe5eedeec-7a74-411d-a83e-895666b36af7' # The url of the race (default is October Pro Qualifier)
model_to_submit = '' # Name of the model you want to submit
##############################


creds = [account_id, username, password]
if __name__ == '__main__':
    from utils.auto_submit_utils import start_selenium
    start_selenium(creds, race_url, model_to_submit, iam_role=True)