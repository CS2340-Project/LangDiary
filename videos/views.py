from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

from .models import LanguageVideo
from .forms import VideoGeneratorForm

import requests
import random
import os
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Get API key from settings
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY

@login_required
def index(request):
    """Main view for the videos app."""
    video_id = request.GET.get('video_id')
    action = request.GET.get('action')
    
    # Get all user's videos
    video_list = LanguageVideo.objects.filter(user=request.user)
        
    # Get current video if specified
    current_video = None
    prev_video_id = None
    next_video_id = None
    
    if video_id:
        current_video = get_object_or_404(LanguageVideo, id=video_id, user=request.user)
        
        # Get previous and next video IDs for navigation
        video_ids = list(video_list.values_list('id', flat=True))
        if video_ids:
            current_index = video_ids.index(int(video_id)) if int(video_id) in video_ids else -1
            
            if current_index > 0:
                prev_video_id = video_ids[current_index - 1]
            
            if current_index < len(video_ids) - 1:
                next_video_id = video_ids[current_index + 1]
    elif video_list.exists():
        # If no specific video is selected but user has videos, show the most recent one
        current_video = video_list.first()
        
        # Get navigation links
        video_ids = list(video_list.values_list('id', flat=True))
        current_index = 0  # First video
        
        if len(video_ids) > 1:
            next_video_id = video_ids[1]
    
    # Initialize video generator form
    form = VideoGeneratorForm()
    
    # Determine if we should show the generator modal
    show_generator = request.GET.get('show_generator') == 'true' or not video_list.exists()
    
    context = {
        'video_list': video_list,
        'current_video': current_video,
        'prev_video_id': prev_video_id,
        'next_video_id': next_video_id,
        'form': form,
        'show_generator': show_generator,
        'is_generating': False,
    }
    
    return render(request, 'videos/index.html', context)

@login_required
@require_POST
def generate_videos(request):
    """Generate a new video based on user language and level preferences."""
    form = VideoGeneratorForm(request.POST)
    
    if form.is_valid():
        language = form.cleaned_data['language']
        level = form.cleaned_data['level']
        
        # Get values from the form or use defaults if not provided
        video_type = form.cleaned_data.get('video_type') or 'lesson'
        duration = form.cleaned_data.get('duration') or 'medium'
        
        try:
            # Build search query based on form data
            search_query = f"{language} language {level} grammar lesson"
            
            # Log the search query for debugging
            logger.info(f"Searching for: {search_query}")
            
            # Check if YOUTUBE_API_KEY is properly set
            if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == 'your_youtube_api_key_here':
                messages.error(request, "YouTube API key is not configured. Please set it in your settings.")
                logger.error("YouTube API key is not properly configured")
                return redirect('videos:index')
            
            # Get already watched YouTube IDs to avoid repeating
            watched_video_ids = list(LanguageVideo.objects.filter(
                user=request.user,
                is_watched=True
            ).values_list('youtube_id', flat=True))
            
            # Add exclusion parameter if we have watched videos
            exclusion_param = ""
            if watched_video_ids:
                # YouTube API doesn't support a direct "NOT IN" query, so we'll request more results and filter
                max_results = 5  # Request more to increase chances of finding unwatched videos
            else:
                max_results = 1
            
            # Call YouTube API - get multiple videos to filter out watched ones
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&type=video&maxResults={max_results}&key={YOUTUBE_API_KEY}"
            logger.info(f"API request URL: {url}")
            
            response = requests.get(url)
            
            # Check response status
            if response.status_code != 200:
                error_message = f"YouTube API returned status code {response.status_code}"
                logger.error(error_message)
                try:
                    error_content = response.json()
                    if 'error' in error_content:
                        error_message += f": {error_content['error'].get('message', '')}"
                except:
                    pass
                messages.error(request, f"Error contacting YouTube API: {error_message}")
                return redirect('videos:index')
            
            data = response.json()
            logger.info(f"API response received: {data.get('pageInfo', {})}")
            
            # Check if we got valid results
            if 'items' in data and data['items']:
                # Filter out already watched videos
                new_items = [item for item in data['items'] if item['id']['videoId'] not in watched_video_ids]
                
                if not new_items:
                    messages.info(request, "You've already watched all the videos from this search. Try different search options.")
                    return redirect('videos:index')
                
                # Randomize selection if we have multiple options
                if len(new_items) > 1:
                    selected_item = random.choice(new_items)
                else:
                    selected_item = new_items[0]
                
                video_id = selected_item['id']['videoId']
                
                # Check if user already has this video but not watched
                existing_video = LanguageVideo.objects.filter(user=request.user, youtube_id=video_id).first()
                if existing_video:
                    messages.info(request, "Showing an existing video from your collection.")
                    return redirect(f'/videos/?video_id={existing_video.id}')
                
                # Get more details about the video
                details_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={video_id}&key={YOUTUBE_API_KEY}"
                details_response = requests.get(details_url)
                
                # Check details response status
                if details_response.status_code != 200:
                    logger.error(f"YouTube API details request returned status code {details_response.status_code}")
                    messages.error(request, "Could not retrieve video details. Please try again.")
                    return redirect('videos:index')
                
                details_data = details_response.json()
                
                if 'items' in details_data and details_data['items']:
                    item = details_data['items'][0]
                    
                    # Determine video type and duration based on video content
                    video_type = 'lesson'  # Default to lesson since we're searching for grammar lessons
                    
                    # Estimate duration from contentDetails
                    duration_str = item['contentDetails'].get('duration', '')
                    if 'PT' in duration_str:
                        if 'H' in duration_str:
                            duration = 'long'
                        elif 'M' in duration_str:
                            minutes = int(duration_str.split('M')[0].split('PT')[1])
                            duration = 'short' if minutes < 5 else 'medium' if minutes < 15 else 'long'
                        else:
                            duration = 'short'
                    else:
                        duration = 'medium'  # Default to medium if we can't determine
                    
                    # Create the video
                    video = LanguageVideo(
                        user=request.user,
                        youtube_id=item['id'],
                        title=item['snippet']['title'],
                        description=item['snippet']['description'],
                        language=language,
                        level=level,
                        video_type=video_type,
                        duration=duration
                    )
                    video.save()
                    
                    # Redirect to the newly created video
                    messages.success(request, "Successfully added a new video to your collection!")
                    return redirect(f'/videos/?video_id={video.id}')
                else:
                    logger.error(f"No items in video details response: {details_data}")
                    messages.error(request, "Could not get details for the video. Please try again.")
            else:
                logger.warning(f"No videos found for query: {search_query}")
                if 'error' in data:
                    logger.error(f"API error: {data['error'].get('message', 'Unknown error')}")
                
                messages.error(request, "No videos found matching your criteria. Try different search options.")
                
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f"An error occurred while searching for videos: {str(e)}")
    else:
        # Log form validation errors
        logger.error(f"Form validation errors: {form.errors}")
        messages.error(request, "Please correct the form errors and try again.")
    
    return redirect('videos:index')

@login_required
@require_POST
def mark_watched(request):
    """Mark a video as watched."""
    video_id = request.POST.get('video_id')
    if not video_id:
        return JsonResponse({'status': 'error', 'message': 'No video ID provided'}, status=400)
    
    try:
        video = get_object_or_404(LanguageVideo, id=video_id, user=request.user)
        video.is_watched = True
        video.save()
        
        return JsonResponse({
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def remove_video(request):
    """Remove a video from user's collection."""
    video_id = request.POST.get('video_id')
    if not video_id:
        return JsonResponse({'status': 'error', 'message': 'No video ID provided'}, status=400)
    
    try:
        video = get_object_or_404(LanguageVideo, id=video_id, user=request.user)
        video.delete()
        
        return JsonResponse({
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def daily_video(request):
    """Show a daily grammar video recommendation."""
    user = request.user
    
    # Get user's preferred language and level from profile (adjust as needed)
    try:
        profile = user.profile
        language = profile.target_language
        level = profile.language_level
    except:
        # Fallback if no profile exists
        language = LanguageVideo.LANGUAGE_CHOICES[0][0]  # Default to first language
        level = LanguageVideo.LEVEL_CHOICES[0][0]  # Default to beginner
    
    # Check if the user has already seen a video today
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Check if user has watched any videos today
    watched_today = LanguageVideo.objects.filter(
        user=user,
        is_watched=True,
        created_at__range=(today_start, today_end)
    ).exists()
    
    if not watched_today:
        # Try to find an unwatched grammar video matching user's preferences
        videos = LanguageVideo.objects.filter(
            user=user,
            language=language,
            level=level,
            is_watched=False,
        ).order_by('?')  # Random selection
        
        if videos.exists():
            # Get a random unwatched video
            video = videos.first()
            # Fix: Use query parameter instead of keyword argument
            return redirect(f'/videos/?video_id={video.id}')
        else:
            # If no unwatched videos, send to generator
            # Fix: Use query parameter
            return redirect('/videos/?show_generator=true')
    else:
        # User has already watched a video today
        messages.info(request, "You've already watched your daily grammar video today. Great job keeping up with your learning!")
        return redirect('videos:index')
    
    # Fallback - should not reach here
    return redirect('videos:index')

# Test view to check if YouTube API is working correctly
@staff_member_required
def test_youtube_api(request):
    """Simple view to test YouTube API connectivity - only accessible to staff."""
    results = {
        'api_key_set': bool(YOUTUBE_API_KEY),
        'api_key_masked': f"{YOUTUBE_API_KEY[:3]}...{YOUTUBE_API_KEY[-3:]}" if YOUTUBE_API_KEY and len(YOUTUBE_API_KEY) > 6 else None,
        'test_status': None,
        'error': None,
        'response': None
    }
    
    if YOUTUBE_API_KEY:
        try:
            # Simple test query
            test_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&maxResults=1&key={YOUTUBE_API_KEY}"
            response = requests.get(test_url)
            
            results['test_status'] = response.status_code
            
            if response.status_code == 200:
                results['response'] = response.json()
            else:
                try:
                    results['error'] = response.json()
                except:
                    results['error'] = response.text
        except Exception as e:
            results['test_status'] = 'Exception'
            results['error'] = str(e)
    
    return HttpResponse(json.dumps(results, indent=2), content_type="application/json")