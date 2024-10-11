import os
import base64
from cryptography.fernet import Fernet
import json

class CityPlanHandler:
    def __init__(self, key=None):
        self.key = self._get_or_generate_key(key)
        self.cipher_suite = Fernet(self.key)

    def _get_or_generate_key(self, key):
        if key is None:
            key = os.environ.get('CITYPLAN_KEY')
            if key is None:
                key = Fernet.generate_key()
                print(f"Generated new key: {key.decode()}")
            else:
                key = self.ensure_valid_key(key)
        else:
            key = self.ensure_valid_key(key)
        return key

    def ensure_valid_key(self, key):
        if isinstance(key, str):
            key = key.encode()
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes long")
        return base64.urlsafe_b64encode(key)

    def save(self, data, filename):
        json_data = json.dumps(data)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        with open(filename, 'wb') as file:
            file.write(b'CITYPLAN' + self.key + encrypted_data)

    def load(self, filename):
        with open(filename, 'rb') as file:
            content = file.read()
        if not content.startswith(b'CITYPLAN'):
            raise ValueError("Not a valid CityPlan file")
        
        key = content[8:40]
        encrypted_data = content[40:]
        
        cipher_suite = Fernet(key)
        
        try:
            json_data = cipher_suite.decrypt(encrypted_data).decode()
            return json.loads(json_data)
        except Exception as e:
            raise ValueError(f"Failed to decrypt the file: {str(e)}")
        
    def export_to_json(self, data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)

    def import_from_json(self, filename):
        with open(filename, 'r') as file:
            return json.load(file)
