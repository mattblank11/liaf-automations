# Import packages
from settings import *

'''
Method: instantiate_mailchimp_api()

Summary: Instantiates Mailchimp API
'''
def instantiate_mailchimp_api():
    return MailChimp(
        os.environ["mailchimp_api_key"],
        os.environ["mailchimp_username"],
    )

'''
Method: get_list_id()

Summary: Retrieves the first list id from Mailchimp API
'''
def get_list_id(
    client
):
  # Get list id
  list_id = client.lists.all(get_all=False)['lists'][0]['id']

  return list_id

'''
Method: get_student_status()

Summary: Retrieves the subscription status for a specific user
'''
def get_student_status(
    client,
    list_id,
    student_email,
):
    # If the student is already in Mailchimp, retrieve their status
    try:
        return client.lists.members.get(
            list_id = list_id,
            subscriber_hash = student_email
        )['status']
    # If the student is not in Mailchimp, return 'subscribed'
    except mailchimp3.Mailchimp.MailChimpError:
        return 'subscribed'

'''
Method: add_student()

Summary: Adds or updates a student information in Mailchimp
'''
def add_student(
    student_data,
):
    # Instantiate MailChimp API
    client = instantiate_mailchimp_api()

    # Get list_id to add member to
    list_id = get_list_id(client)

    # Get student 'status' if student is already in Mailchimp
    status = get_student_status(
        client,
        list_id,
        student_data['student_email']
    )

    # Create data payload for member
    member_data = {
        'email_address': student_data['student_email'],
        'status_if_new': status,
        'status': status,
        'merge_fields': {
            'FNAME': student_data['student_first_name'] or '',
            'LNAME': student_data['student_last_name'] or '',
            'NEXTDESC': student_data["next_lecture_description"] or '',
            'NEXTMINS': student_data["next_lecture_minutes"] or '',
            'NEXTLINK': student_data["next_lecture_link"] or '',
            'COURSENAME': student_data["course_name"] or '',
            'LSTLCTDATE': student_data["last_lecture_date"] or '',
        }
    }

    # Add student data to Mailchimp
    client.lists.members.create_or_update(
        list_id = list_id,
        subscriber_hash = student_data['student_email'],
        data = member_data,
    )

    # Add tags to student
    client.lists.members.tags.update(
        list_id = list_id,
        subscriber_hash = student_data['student_email'],
        data = {
            'tags': student_data["tags"],
        },
    )
