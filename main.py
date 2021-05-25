from flask import Flask, jsonify, request
from threading import Thread
from flask_restful import Resource, Api
import json

# Import packages from teachable_webhooks
from teachable_webhooks import (
  course_enrollment,
  course_completion,
  lecture_completion,
)

app = Flask('')
api = Api(app)

# Home
class home(Resource):
  def get(self):
    return jsonify({'Hello': 'world!'})

# New enrollment in Teachable
class teachable_new_enrollment(Resource):
  def post(self):
    data = json.loads(request.get_data().decode('latin1'))[0]

    # Run code for new enrollment
    response = course_enrollment(
      data,
    )
    
    print('\nNew Enrollment')
    print(response)

    return jsonify(response)

# Course completed in Teachable
class teachable_course_completed(Resource):
  def post(self):
    data = json.loads(request.get_data().decode('latin1'))[0]
  
    # Run code for course completion
    response = course_completion(
      data,
    )
    
    print('\nCourse Completed')
    print(response)

    return jsonify(response)
  
# Lecture completed in Teachable
class teachable_lecture_completed(Resource):
  def post(self):
    data = json.loads(request.get_data().decode('latin1'))[0]
  
    # Run code for course completion
    response = lecture_completion(
      data,
    )
    
    print('\nLecture Completed')
    print(response)

    return jsonify(response)

## API Endpoints
# Home
api.add_resource(
  home,
  '/',
)
# New Enrollment
api.add_resource(
  teachable_new_enrollment,
  '/api/teachable/new-enrollment',
)
# Course Completion
api.add_resource(
  teachable_course_completed,
  '/api/teachable/course-completed',
)
# Lecture Completion
api.add_resource(
  teachable_lecture_completed,
  '/api/teachable/lecture-completed',
)

def run():
  app.run(
    host = '0.0.0.0',
    port = 8000,
  )

t = Thread(target=run)
t.start()