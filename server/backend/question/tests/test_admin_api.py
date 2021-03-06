from datetime import date

from rest_framework import status

from question.models import Poll, Question

from .init_class import InitClass
import json
from question.models import Question

# Тесты не проверяют опасных ситуаций 
# Но в реальном проекте я бы их точно прописал 
class TestAdminAPI(InitClass):

    def setUp(self):
        pass


    def test_pool_api(self):

        default_user, default_client = self.create_user()
        admin_user, admin_client = self.create_super_user()
       
        another_user_data = {"username": 'AnotherUser', 
                            "email": 'anotheruser@gmail.com', 
                            "password": 'PaSwOrD123'}
        another_user, another_user_client = self.data_create_user(data=another_user_data)
        another_user.report_id = 4321 
        another_user.save() 

        # Default user try get pool list
        response = self.get_poll(default_client)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin user try get pool list 
        response = self.get_poll(admin_client)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        poll_data = {
                "name": "New Test Poll",
                "description": "New Test Poll",
                "date_start": "2020-09-23",
                "date_end": "2020-10-31",
                "questions_list": [
                    {
                        "text": "How many u drink?",
                        "question_type": "TEXT_RESPONSE",
                        
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

        # Check QuestionViewSet API logic 
        response, poll_model = self.create_poll(admin_client, data=poll_data)
        default_user.report_id = 1234
        default_user.save()
        
        question_data =  {
                "poll": poll_model.pk, 
                "question_type": "MULTIPLE_CHOICE_ANSWER",
                "text": "Added of question",
                "answer_choices": {
                    "1": "Add first answer",
                    "2": "Add secont answer"
                }
            }
        
        # User try create question 
        response, _ = self.create_quiestion(default_client, question_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin tre create question 
        response, question_model = self.create_quiestion(admin_client, question_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['question_type'], "MULTIPLE_CHOICE_ANSWER")

        change_question_data =  {
                "question_type": "MULTIPLE_CHOICE_ANSWER",
                "text": "Changed Added of question",
                "answer_choices": {
                    "1": "Changed Add first answer",
                    "2": "Changed Add secont answer"
                }
            }
        # User try change question 
        response, _ = self.change_quiestion(default_client, change_question_data, question_model.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admint change question 
        response, question_model = self.change_quiestion(admin_client, change_question_data, question_model.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        questoins = Question.objects.all()
        # Check craete Report Logic
        report_data = {
            "poll": poll_model.pk,
            "answers_list": [
                {
                "answer": "First answer",
                "question": questoins[0].pk
                },
                {
                "answer": "1 2",
                "question":  questoins[1].pk
                }
            ]
            }
        
        # Anon user create report
        anon_client = self.anon_client() 
        response, report_model = self.create_report(default_client, report_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        report_data_with_id = {
            "poll": poll_model.pk,
            "user_report_id": another_user.report_id,
            "answers_list": [
                {
                "answer": "First answer",
                "question": questoins[0].pk
                },
                {
                "answer": "1 2",
                "question":  questoins[1].pk
                }
            ]
            }
        # Anon usre cant create report with user_report_id 
        response, report_model = self.create_report(default_client, report_data_with_id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # user try create report not with his id    
        response, report_model = self.create_report(default_client, report_data_with_id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

