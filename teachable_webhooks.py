# Import packages
from settings import *
from mailchimp import (
    add_student,
)
from google_sheets import (
    get_data_from_s3,
    update_csv,
)
from slack import (
    post_to_slack,
    create_slack_message,
)

'''
Method: course_enrollment()

Summary: Runs all the code for new course enrollments
'''
def course_enrollment(
    data,
):
    # Get pertinent data from webhook
    course_enrollment_data = parse_enrollment_data(
        data
    )

    # Post message in Slack
    message_data = {
        'Name': 'student_name',
        'Email': 'student_email',
        'Course': 'course_name',
        'Amount': 'payment',
    }
    message = create_slack_message(
        'COURSE ENROLLMENT',
        course_enrollment_data,
        message_data,
    )

    # Post message to slack
    post_to_slack(message)

    # Get the info for the first lecture the student needs to watch
    course_enrollment_data = get_first_lecture_info(
        data,
        course_enrollment_data,
    )

    # Update csv
    update_csv(
        'Sign Ups',
        course_enrollment_data,
    )

    # Add tags to lecture_completion_data
    course_enrollment_data['tags'] = [
        {
            'name': course_enrollment_data['course_name'],
            'status': 'active',
        },
        {
            'name': 'Not Started',
            'status': 'active',
        },
        {
            'name': 'New Sign Up',
            'status': 'active',
        },
    ]

    # Create / Update student in Mailchimp
    add_student(
        course_enrollment_data,
    )

    return course_enrollment_data


'''
Method: course_completion()

Summary: Runs all the code for course completions
'''
def course_completion(
    data,
):
    # Get pertinent data from webhook
    course_enrollment_data = parse_enrollment_data(data)

    # Post message in Slack
    message_data = {
        'Name': 'student_name',
        'Email': 'student_email',
        'Course': 'course_name',
    }
    message = create_slack_message(
        'COURSE COMPLETION',
        course_enrollment_data,
        message_data,
    )

    # Post message to slack
    post_to_slack(message)

    # Get the info for the first lecture the student needs to watch
    course_enrollment_data = get_first_lecture_info(
        data,
        course_enrollment_data,
    )

    # Update csv
    update_csv(
        'Completed Courses',
        course_enrollment_data,
    )

    # Add tags to lecture_completion_data
    course_enrollment_data['tags'] = [
        {
            'name': course_enrollment_data['course_name'],
            'status': 'active',
        },
        {
            'name': 'Completed Course',
            'status': 'active',
        },
        {
            'name': 'In Progress',
            'status': 'inactive',
        },
    ]

    # Create / Update student in Mailchimp
    add_student(
        course_enrollment_data,
    )

    return course_enrollment_data

'''
Method: lecture_completion()

Summary: Runs all the code for lecture completions
'''
def lecture_completion(
    data,
):
    # Get pertinent data from webhook
    lecture_completion_data = parse_lecture_completion_data(data)

    # Post message in Slack
    message_data = {
        'Name': 'student_name',
        'Email': 'student_email',
        'Course': 'course_name',
        'Lecture': 'lecture_name',
        'Percentage Complete': 'percent_complete',
    }
    message = create_slack_message(
        'LECTURE COMPLETION',
        lecture_completion_data,
        message_data,
    )

    # Post message to slack
    post_to_slack(message)

    # Get the info for the first lecture the student needs to watch
    lecture_completion_data = get_first_lecture_info(
        data,
        lecture_completion_data,
    )

    # Update csv
    update_csv(
        'Completed Lectures',
        lecture_completion_data,
    )

    # Add tags to lecture_completion_data
    lecture_completion_data['tags'] = [
        {
            'name': lecture_completion_data['course_name'],
            'status': 'active',
        },
        {
            'name': 'In Progress',
            'status': 'active',
        },
        {
            'name': 'Not Started',
            'status': 'inactive',
        },
        {
            'name': 'New Sign Up',
            'status': 'inactive',
        },
    ]

    # Create / Update student in Mailchimp
    add_student(
        lecture_completion_data,
    )

    return lecture_completion_data

'''
Method: parse_enrollment_data()

Summary: Gets enrollment information from the Teachable webhook
'''
def parse_enrollment_data(
    data
):
  student_name = data['object']['user']['name']
  split_name_info = split_name(student_name)
  first_name = split_name_info['first_name']
  last_name = split_name_info['last_name']
  student_email = data['object']['user']['email']
  course_id = data['object']['course']['id']
  course_name = data['object']['course']['name']
  payment = data['object']['user']['transactions_gross'] / 100
  promo_code = data['object']['coupon']
  signup_datetime = data['created']

  return {
    'student_name': student_name,
    'student_first_name': first_name,
    'student_last_name': last_name,
    'student_email': student_email,
    'course_id': course_id,
    'course_name': course_name,
    'payment': payment,
    'promo_code': promo_code,
    'signup_datetime': signup_datetime,
    'last_lecture_date': dt.datetime.now().strftime('%m/%d/%Y')
  }

'''
Method: parse_lecture_completion_data()

Summary: Gets lecture completion information from the Teachable webhook
'''
def parse_lecture_completion_data(
    data
):
  student_name = data['object']['user']['name']
  split_name_info = split_name(student_name)
  first_name = split_name_info['first_name']
  last_name = split_name_info['last_name']
  student_email = data['object']['user']['email']
  course_id = data['object']['course']['id']
  course_name = data['object']['course']['name']
  lecture_name = data["object"]["lecture"]["name"]
  percent_complete = data["object"]["percent_complete"]
  timestamp = data["created"]

  return {
    'student_name': student_name,
    'student_first_name': first_name,
    'student_last_name': last_name,
    'student_email': student_email,
    'course_id': course_id,
    'course_name': course_name,
    'lecture_name': lecture_name,
    'percent_complete': percent_complete,
    'timestamp': dt.datetime.strptime(timestamp[:10], '%Y-%m-%d').strftime('%m/%d/%Y'),
    'last_lecture_date': dt.datetime.now().strftime('%m/%d/%Y')
  }

'''
Method: get_first_lecture_info()

Summary: Gets information about the first lecture the student has to take
'''
def get_first_lecture_info(
    data,
    course_enrollment_data,
):
    # Get the data about all the lectures
    lecture_df = get_data_from_s3(
        os.environ['liaf_s3_bucket'],
        'Course Videos',
    )

    # Filter the lecture_df to the course the student is taking
    current_course_id = course_enrollment_data['course_id']
    
    lecture_df = lecture_df[lecture_df['Course Code'] == current_course_id]

    # Get the information about the next lecture's description, minutes, and link
    next_lecture_description = lecture_df.loc[
        lecture_df['Course Video'] == 1,
        'Video About',
    ].values[0]

    next_lecture_minutes = int(
        lecture_df.loc[
            lecture_df['Course Video'] == 1,
            'Video Minutes',
        ].values[0]
    )

    next_lecture_link = lecture_df.loc[
        lecture_df['Course Video'] == 1,
        'Lecture Link'
    ].values[0]

    # Add next_lecture_description, next_lecture_minutes, and next_lecture_link to course_enrollment_data
    course_enrollment_data['next_lecture_description'] = next_lecture_description
    course_enrollment_data['next_lecture_minutes'] = next_lecture_minutes
    course_enrollment_data['next_lecture_link'] = next_lecture_link

    # Return course_enrollment_data
    return course_enrollment_data

'''
Method: get_next_lecture_info()

Summary: Gets information about the next lecture the student has to take
'''
def get_next_lecture_info(
    data,
    lecture_completion_data,
):
    # If the student completed the course, return empty strings
    if data['object']['percent_complete'] == 100:
        lecture_completion_data['next_lecture_description'] = 'Congrats on finishing the course!'
        lecture_completion_data['next_lecture_minutes'] = 0
        lecture_completion_data['next_lecture_link'] = 'likeiamfive.teachable.com'

        return lecture_completion_data

    # Get the data about all the lectures
    lecture_df = get_csv_from_s3(
        os.environ['liaf_s3_bucket'],
        'Course Videos',
    )

    # Filter the lecture_df to the course the student is taking
    current_course_id = data['object']['course_id']
    current_lecture_id = data['object']['lecture_id']
    
    lecture_df = lecture_df[lecture_df['Course Code'] == current_course_id]

    # Get the video # for the current lecture
    current_lecture_number = lecture_df.loc[
        lecture_df['Lecture Code'] == current_lecture_id,
        'Course Video'
    ].values[0]

    next_lecture_number = current_lecture_number + 1

    # Get the information about the next lecture's description, minutes, and link
    next_lecture_description = lecture_df.loc[
        lecture_df['Course Video'] == next_lecture_number,
        'Video About',
    ].values[0]

    next_lecture_minutes = int(
        lecture_df.loc[
            lecture_df['Course Video'] == next_lecture_number,
            'Video Minutes',
        ].values[0]
    )

    next_lecture_link = lecture_df.loc[
        lecture_df['Course Video'] == next_lecture_number,
        'Lecture Link'
    ].values[0]

    # Add next_lecture_description, next_lecture_minutes, and next_lecture_link to lecture_completion_data
    lecture_completion_data['next_lecture_description'] = next_lecture_description
    lecture_completion_data['next_lecture_minutes'] = next_lecture_minutes
    lecture_completion_data['next_lecture_link'] = next_lecture_link

    # Return lecture_completion_data
    return lecture_completion_data

'''
Method: split_name()

Summary: Splits name into first and last
'''
def split_name(name):
  first_name = name.split(" ")[0]
  last_name = name.split(" ")[1] if len(name.split(" ")) > 1 else ''

  return {
    'first_name': first_name,
    'last_name': last_name,
  }