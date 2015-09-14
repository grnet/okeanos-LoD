# coding=utf8
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

class TestApplication(APITestCase):
    def __init__(self):
        self.unauthorized_response_status = status.HTTP_401_UNAUTHORIZED
        self.unauthorized_response_data = {'status': 401,
                                           'errors': [{
                                               'detail': "Unauthorized. Request failed because user "
                                                         "provided an invalid token."
                                           }]}

    def setUp(self):
        pass

    # Test for uploading an application.
    def test_application_upload(self):
        application_file = SimpleUploadedFile("application.jar",
                                              "test12345@#%^!@(*^$@!*(""&^!@∂¨ˆ•¡™¶ª©∆˚ß"
                                              "ƒå¬åµ˜∂˜ˆ¨˙£™®¨˜ß∂√©¨ˆ™˙£∫®¨∂å©ƒ™ø`ˆ¨")

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + "invalid-token")
        response = self.client.post("/api/apps/",
                                    {'description': "My application",
                                     'file': application_file,
                                     'project_name': 'lambda.grnet.gr'})

        self.assertEqual(response.status_code, self.unauthorized_response_status)
        self.assertEqual(response.data, self.unauthorized_response_data)

        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/apps/",
                                    {'description': "My application",
                                     'file': application_file,
                                     'project_name': 'lambda.grnet.gr'})

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)



#    def test_file_upload(self):
#        response = self.upload_test_file("test_file_upload")
#        self.assertEqual(response.status_code, 201)

#    def test_list_files(self):
#        self.upload_test_file(name="test_file_list")
#        response = self.client.get('/backend/user_files')
#        self.assertEqual(response.data[0]['name'], u'test_file_list')

#    def test_delete_file(self):
#        self.upload_test_file(name="test_file_delete")
#        response = self.client.get('/backend/user_files')
#        uuid = response.data[0]['uuid']
#        self.client.delete('/backend/user_files', {'uuid': uuid})
#        response = self.client.get('/backend/user_files')
#        self.assertEqual(len(response.data), 0)
