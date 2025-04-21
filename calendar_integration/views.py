import os
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

import google
from django.shortcuts import redirect, render
from django.conf import settings
from django.urls import reverse
from django.utils.dateparse import parse_date
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from django.http import HttpResponse
from google.oauth2.credentials import Credentials

from calendar_integration.models import GoogleCredentials

CLIENT_SECRETS_CONFIG = settings.GOOGLE_CLIENT_SECRET_JSON
SCOPES = settings.GOOGLE_CALENDAR_SCOPES

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def oauth2login(request):
    print(request.build_absolute_uri(reverse('calendar_integration:oauth2callback')))
    flow = Flow.from_client_config(
        CLIENT_SECRETS_CONFIG,
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('calendar_integration:oauth2callback'))
    )

    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    request.session['state'] = state

    return redirect(authorization_url)

def oauth2callback(request):
    state = request.session['state']
    flow = Flow.from_client_config(
        CLIENT_SECRETS_CONFIG,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(reverse('calendar_integration:oauth2callback'))
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    if not flow.credentials:
        return HttpResponse("Failed to authenticate.", status=400)

    credentials = flow.credentials

    GoogleCredentials.objects.update_or_create(
        user=request.user,
        defaults={
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': json.dumps(credentials.scopes),
        }
    )

    return redirect('users.profile')

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
    credentials = GoogleCredentials.objects.filter(user=request.user).first()
    if not credentials:
        return redirect('calendar_integration:oauth2login')

    credentials = credentials_to_dict(credentials)

    credentials = Credentials(
        token=credentials['token'],
        refresh_token=credentials.get('refresh_token'),
        token_uri=credentials['token_uri'],
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        scopes=credentials['scopes']
    )

    prompt = request.GET.get('prompt', 'Exercise Deadline')
    deadline_str = request.GET.get('deadline')
    exercise_id = request.GET.get('exercise_id')

    try:
        deadline = datetime.strptime(deadline_str, "%B %d, %Y").date()
    except (ValueError, TypeError):
        return HttpResponse("Invalid deadline format", status=400)

    # Convert date to datetime for Google Calendar API
    start_datetime = datetime.combine(deadline, datetime.min.time())  # 00:00
    end_datetime = start_datetime + timedelta(hours=1)

    # You can adjust the time zone as needed
    timezone = 'America/New_York'

    event = {
        'summary': prompt,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': timezone,
        },
    }

    # Call Google Calendar API
    service = build('calendar', 'v3', credentials=credentials)
    event = service.events().insert(calendarId='primary', body=event).execute()

    query_string = urlencode({
        'calendar_success': '1' if event else '0',
        'event_url': event.get("htmlLink") if event else '',
    })

    base_url = reverse('exercises:create_page', args=[exercise_id])
    return redirect(f"{base_url}?{query_string}")


def get_user_credentials(user):
    try:
        creds_obj = GoogleCredentials.objects.get(user=user)
        creds = creds_obj.to_credentials()

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            creds_obj.token = creds.token
            creds_obj.save()

        return creds

    except GoogleCredentials.DoesNotExist:
        return None