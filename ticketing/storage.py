"""
Custom storage backend for secure file attachments.
Files stored here are not publicly accessible via web server.
"""
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class SecureFileStorage(FileSystemStorage):
    """
    Storage backend that stores files in a secure location
    outside the public media directory.
    """
    
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.SECURE_MEDIA_ROOT
        # base_url is None to prevent public URL generation
        super().__init__(location=location, base_url=None)
    
    def url(self, name):
        """
        Override url() to return None or raise an error.
        Files should only be accessed through the secure download view.
        """
        return None

