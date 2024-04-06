import requests
from django.conf import settings
from .models import FblAccount

def fbl_auth_request_code(badge_number: int, dob: str) -> bool:
    res = requests.post(f'{settings.FBL_AUTH_SERVER}/auth/get-code', data={
        "badge": badge_number,
        "password": dob
    })
    if res.status_code != 201:
        print(res.status_code)
        return False
    return True

def fbl_auth_validate_code(badge_number: str, dob: str, validation_code: str) -> str | None:
    res = requests.post(f'{settings.FBL_AUTH_SERVER}/auth/signin', json={
        "badge": badge_number,
        "password": dob,
        "code": validation_code
    })
    if res.status_code != 201:
        print(res.status_code)
        return None
    
    return res.json()["accessToken"]

def fbl_auth_get_account(jwt_token: str) -> dict[str, str] | None:
    res = requests.get(f'{settings.FBL_AUTH_SERVER}/attendees/me', headers={
        "Authorization": f"Bearer {jwt_token}" 
    })
    if res.status_code != 200:
        print(res.status_code)
        return None
    
    return res.json()

def get_or_create_account(account_info: dict[str, str]) -> FblAccount:
    """Get or create a FblAccount object based on the account info"""
    if FblAccount.objects.filter(account_id=account_info["account_id"]).exists():
        # Get existing user and update status
        user = FblAccount.objects.get(account_id=account_info["account_id"])
        user.status = account_info["status"]
        user.save()
        return user
    
    # Create new user with (generic) username
    user = FblAccount.create_user(account_info["username"])
    return FblAccount.objects.create(
        user=user,
        badge_number=account_info["badge"],
        account_id=account_info["account_id"],
        status=account_info["status"],
        username=account_info["username"],
        tags_secured=','.join(account_info["tags_secured"])
    )