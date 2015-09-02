# coding=utf8
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.models import User


class TestFileUpload(APITestCase):
    def setUp(self):
        self.user = User.objects.create(uuid='209230923ur92r029u3r')
        self.client.force_authenticate(user=self.user)

    def test_file_upload(self):
        file_to_upload = SimpleUploadedFile("test_upload_file",
                                            "test12345@#%^!@(*^$@!*(""&^!@∂¨ˆ•¡™¶ª©∆˚ß"
                                            "ƒå¬åµ˜∂˜ˆ¨˙£™®¨˜ß∂√©¨ˆ™˙£∫®¨∂å©ƒ™ø`ˆ¨")
        response = self.client.put('/backend/user_files',
                                   {'file': file_to_upload},
                                   format='multipart')

        self.assertEqual(response.status_code, 201)

    def test_list_files(self):
        self.test_file_upload()
        response = self.client.get('/backend/user_files')
        self.assertEqual(response.data[0]['name'], u'test_upload_file')

    def test_delete_file(self):
        self.test_file_upload()
        response = self.client.get('/backend/user_files')
        id = response.data[0]['id']
        self.client.delete('/backend/user_files', {'id': id})
        response = self.client.get('/backend/user_files')
        self.assertEqual(len(response.data), 0)
