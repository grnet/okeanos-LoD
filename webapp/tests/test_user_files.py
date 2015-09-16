# coding=utf8
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.models import User


# class TestFileUpload(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create(uuid='209230923ur92r029u3r')
#         self.client.force_authenticate(user=self.user)
#
#     def upload_test_file(self, name):
#         file_to_upload = SimpleUploadedFile(name,
#                                             "test12345@#%^!@(*^$@!*(""&^!@∂¨ˆ•¡™¶ª©∆˚ß"
#                                             "ƒå¬åµ˜∂˜ˆ¨˙£™®¨˜ß∂√©¨ˆ™˙£∫®¨∂å©ƒ™ø`ˆ¨")
#         response = self.client.put('/backend/user_files',
#                                    {'file': file_to_upload},
#                                    format='multipart')
#         return response
#
#     def test_file_upload(self):
#         response = self.upload_test_file("test_file_upload")
#         self.assertEqual(response.status_code, 201)
#
#     def test_list_files(self):
#         self.upload_test_file(name="test_file_list")
#         response = self.client.get('/backend/user_files')
#         self.assertEqual(response.data[0]['name'], u'test_file_list')
#
#     def test_delete_file(self):
#         self.upload_test_file(name="test_file_delete")
#         response = self.client.get('/backend/user_files')
#         uuid = response.data[0]['uuid']
#         self.client.delete('/backend/user_files', {'uuid': uuid})
#         response = self.client.get('/backend/user_files')
#         self.assertEqual(len(response.data), 0)
