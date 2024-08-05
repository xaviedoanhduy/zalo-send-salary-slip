from odoo import models, fields, api
import base64
import requests
import json
import tempfile
import os


class ZaloIntegration(models.Model):
    _name = 'zalo.integration'
    _description = 'Zalo Integration'

    access_token = fields.Char(string='Zalo Access Token', required=True)

    def upload_file_to_zalo(self, file_content, file_name):
        url = "https://openapi.zalo.me/v2.0/oa/upload/file"
        headers = {"access_token": self.access_token}

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {'file': (file_name, file, 'application/pdf')}
                response = requests.post(url, headers=headers, files=files)

            if response.status_code == 200:
                return response.json().get('data', {}).get('token')
            else:
                raise Exception(f"Failed to upload file. Status code: {response.status_code}")
        finally:
            os.unlink(temp_file_path)

    def send_zalo_message(self, user_id, message, file_token=None):
        url = "https://openapi.zalo.me/v3.0/oa/message/cs"
        headers = {
            "access_token": self.access_token,
            "Content-Type": "application/json"
        }

        payload = {
            "recipient": {"user_id": user_id},
            "message": {"text": message}
        }

        if file_token:
            payload["message"]["attachment"] = {
                "type": "file",
                "payload": {"token": file_token}
            }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            raise Exception(f"Failed to send message. Status code: {response.status_code}")
