from http.client import HTTPException


class MissingReferencedDataException(HTTPException):
    def __init__(self, missing_users, missing_channels):
        self.missing_users = missing_users
        self.missing_channels = missing_channels
    
    def to_content(self):
        return {
            'missing_users': self.missing_users,
            'missing_channels': self.missing_channels
        }
