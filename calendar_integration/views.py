import os
import json

import google
from django.shortcuts import redirect, render
from django.conf import settings
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from django.http import HttpResponse
from google.oauth2.credentials import Credentials

CLIENT_SECRETS_FILE = settings.GOOGLE_CLIENT_SECRET_JSON
SCOPES = settings.GOOGLE_CALENDAR_SCOPES
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def oauth2login(request):
    print(request.build_absolute_uri(reverse('calendar_integration:oauth2callback')))
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('calendar_integration:oauth2callback'))
    )

    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    request.session['state'] = state

    return redirect(authorization_url)

def oauth2callback(request):
    state = request.session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(reverse('calendar_integration:oauth2callback'))
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    if not flow.credentials:
        return HttpResponse("Failed to authenticate.", status=400)

    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('calendar_integration:add_event')

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def add_event(request):
    credentials = request.session.get('credentials')
    if not credentials:
        return redirect('calendar_integration:oauth2login')

    credentials = Credentials(
        token=credentials['token'],
        refresh_token=credentials.get('refresh_token'),
        token_uri=credentials['token_uri'],
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        scopes=credentials['scopes']
    )

    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': 'Exercise Deadline',
        'start': {
            'dateTime': '2025-04-30T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2025-04-30T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()

    return HttpResponse(f'Event created: {event.get("htmlLink")}')