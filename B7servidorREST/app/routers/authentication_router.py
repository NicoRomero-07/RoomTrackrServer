from fastapi import APIRouter, HTTPException, Header
import google_auth_oauthlib
from google.oauth2.credentials import Credentials
from pydantic import BaseModel
import requests
from googleapiclient.discovery import build
import json

router = APIRouter()


class Code(BaseModel):
    code: str


def validate_access_token(access_token):
    params = {"access_token": access_token}
    response = requests.get("https://oauth2.googleapis.com/tokeninfo", params=params)
    if response.status_code != 200:
        return False
    return True


def oauth2_scheme(access_token: str = Header()):
    if not validate_access_token(access_token):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return access_token


@router.post("/login")
async def login(code: Code):
    try:
        # Create an OAuth2 flow object
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            "client_secret.json",
            scopes=[
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "openid",
            ],
            state="xyz123",
        )
        flow.redirect_uri = "http://localhost:3000"
        flow.fetch_token(code=code.code)
        tokens = flow.credentials
        f = open("client_secret.json", "r")
        secrets = json.loads(f.read())
        CLIENT_ID = secrets["web"]["client_id"]
        CLIENT_SECRET = secrets["web"]["client_secret"]
        # Closing file
        f.close()
        creds = Credentials.from_authorized_user_info(
            info={
                "access_token": tokens.token,
                "refresh_token": tokens.refresh_token,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        )
        profile_data = {}
        with build("people", "v1", credentials=creds) as service:
            profile_data = (
                service.people()
                .get(
                    resourceName="people/me",
                    personFields="birthdays,locations,genders,emailAddresses,coverPhotos,nicknames,names,phoneNumbers,photos,addresses",
                )
                .execute()
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"access_token": tokens.token, "profile_data": profile_data}
