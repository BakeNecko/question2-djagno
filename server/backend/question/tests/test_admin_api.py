from datetime import date

from rest_framework import status

from question.models import Poll, Question

from .init_class import InitClass
import json

class TestAdminAPI(InitClass):

  def test_pool_api(self):
    default_user, default_client = self.create_user()
    admin_user, admin_client = self.create_super_user()
    
    # Default user try get pool list
    response = self.get_poll(default_client)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Admin user try get pool list 
    response = self.get_poll(admin_client)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    poll_data = {
            "name": "New Test Poll",
            "description": "New Test Poll",
            "date_start": "2020-05-23",
            "date_end": "2020-05-31",
            "questions": [
                {
                    "text": "How many u drink?",
                    "question_type": "TEXT_RESPONSE"
                },
                {
                    "text": "New Questoin",
                    "question_type": "MULTIPLE_CHOICE_ANSWER",
                    "answer_choices": {
                        "1": "first answer",
                        "2": "secont answer"
                    }
                }
            ]
            }
    # Default user try post(create) poll : he cant do it this 
    response, _ = self.create_poll(default_client, data=poll_data)
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Admin craete poll
    response, poll = self.create_poll(admin_client, data=poll_data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(poll.name, 'New Test Poll')
    self.assertEqual(poll.description, 'New Test Poll')
    # User try update poll
    poll_change_data = {
              "name": "Change Test Pool",
              "description": " Change New Test Poll",
              "date_end": "2020-05-26"
            }

    response, _ = self.update_poll(default_client, data=poll_change_data, pk=poll.pk)
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #Admin update poll
    response, poll = self.update_poll(admin_client, data=poll_change_data, pk=poll.pk)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # User try delete poll
    response = self.delete_poll(default_client, poll.pk)
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Admin try delete poll 
    response = self.delete_poll(admin_client, pk=poll.pk)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
