from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import (APIClient, APIRequestFactory, APITestCase,
                                 URLPatternsTestCase, force_authenticate)
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

from question.models import Poll, Report, Question

class InitClass(APITestCase, URLPatternsTestCase):
    User = get_user_model()

    urlpatterns = [
        path('api/v1/', include('question.urls')),
    ]


    def create_user(self):
        user = self.User.objects.create(username='TestUser', 
                                        email='testuser@gmail.com', 
                                        password='PaSwOrD123')
        access = AccessToken.for_user(user)
        client = self.login_user(access)
        return user, client

    def data_create_user(self,data):
        user = self.User.objects.create(**data)
        access = AccessToken.for_user(user)
        client = self.login_user(access)

        return user, client
        
    def create_anon_user(self):
        client = APIClient()
        return client

    def create_super_user(self):
        user = self.User.objects.create(username='AdminTestUser', 
                                        email='admintestuser@gmail.com', 
                                        password='PaSwOrD123', 
                                        is_staff=True)
        access = AccessToken.for_user(user)
        client = self.login_user(access)
        return user, client 

    def login_user(self, token):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' +
                           str(token))  # simpulator logined user
        return client

    def get_poll(self, client):
        path = reverse('poll')
        response = client.get(path)
        return response

    def update_poll(self, client, data, pk):
        path = reverse('poll_detail', args=[pk])
        response = client.put(path, data=data, format='json')
        try:
            model = Poll.objects.get(pk=response.data['id'])
        except:
            model = None
        return response, model

    def create_poll(self, client, data):
        path = reverse('poll')
        response = client.post(path, data=data, format='json')
        try:
            model = Poll.objects.get(pk=response.data['id'])
        except:
            model = None
        return response, model

    def delete_poll(self, client, pk):
        path = reverse('poll_detail', args=[pk])
        response = client.delete(path)
        try:
            model = Poll.objects.get(pk=response.data['id'])
            raise Exception('Poll was not deleted')
        except:
            model = None
        return response

    def create_report(self, client, data):
        path = reverse('report')
        response = client.post(path, data=data, format='json')
        try:
            model = Report.objects.get(pk=response.data['id'])
        except:
            model = None
        return response, model    
    
    def create_quiestion(self, client, data):
        path = reverse('question')
        response = client.post(path, data=data, format='json')
        try:
            model = Question.objects.get(pk=response.data['id'])
        except:
            model = None
        return response, model 

    def change_quiestion(self, client, data, pk):
        path = reverse('question_detail', args=[pk])
        response = client.put(path, data=data, format='json')
        try:
            model = Question.objects.get(pk=response.data['id'])
        except:
            model = None
        return response, model 


