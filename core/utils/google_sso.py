from dataclasses import dataclass
from typing import Any, Optional

from django.utils.translation import gettext_lazy as _
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from django.conf import settings


@dataclass
class GoogleSSO:
    _flow: Optional[Flow] = None
    _userinfo: Optional[dict[Any, Any]] = None

    @staticmethod
    def get_client_config() -> Credentials:
        return {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "project_id": settings.GOOGLE_OAUTH_PROJECT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
            }
        }

    @property
    def flow(self) -> Flow:
        if not self._flow:
            self._flow = Flow.from_client_config(
                self.get_client_config(),
                scopes=settings.GOOGLE_OAUTH_SCOPES,
                redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
            )
        return self._flow

    def get_user_info(self) -> dict:
        session = self.flow.authorized_session()
        user_info = session.get(
            "https://www.googleapis.com/oauth2/v2/userinfo").json()
        return user_info

    def get_user_token(self):
        return self.flow.credentials.token
