# Import packages
from settings import *

'''
Method: post_to_slack()

Summary: Posts a message to slack
'''
def post_to_slack(message):
  payload = {
    'text': message,
  }

  r = requests.post(
    os.environ['slack_url'],
    headers = {
      'Content-Type': 'application/json',
    },
    data = json.dumps(payload),
  )

  return r.content

'''
Method: create_slack_message()

Summary: Creates Slack message from payloaf
'''
def create_slack_message(
    action,
    student_data,
    message_data,
):
    message = f'<!channel> *{action.upper()}*'
    
    for field in message_data:
      message += f'\n*{field}:* {student_data[message_data[field]]}'
    
    return message
