from http.client import HTTPException


class MissingReferencedDataException(HTTPException):
    def __init__(self, missing_members, missing_channels):
        self.missing_members = missing_members
        self.missing_channels = missing_channels
    
    def to_content(self):
        return {
            'missing_members': self.missing_members,
            'missing_channels': self.missing_channels
        }
