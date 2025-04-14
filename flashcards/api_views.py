# flashcards/api_views.py
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Flashcard

@login_required
def get_card(request, card_id):
    """API endpoint to get a single flashcard data"""
    try:
        flashcards = Flashcard.objects.filter(user=request.user).order_by('num_revisions')
        current_card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        
        # Get index of current card
        flashcard_list = list(flashcards)
        current_card_index = flashcard_list.index(current_card)
        
        # Set previous and next IDs
        prev_card_id = flashcards[current_card_index - 1].id if current_card_index > 0 else None
        next_card_id = flashcards[current_card_index + 1].id if current_card_index < len(flashcards) - 1 else None
        
        # Return card data as JSON
        return JsonResponse({
            'id': current_card.id,
            'front_text': current_card.front_text,
            'back_text': current_card.back_text,
            'num_revisions': current_card.num_revisions,
            'prev_id': prev_card_id,
            'next_id': next_card_id
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
            
@login_required
def get_indicators(request):
    """API endpoint to get the card progress indicators HTML"""
    flashcards = Flashcard.objects.filter(user=request.user).order_by('num_revisions')
    
    # Get current card ID from query params
    current_card_id = request.GET.get('card_id')
    current_card = None
    
    if current_card_id:
        try:
            current_card = flashcards.get(id=current_card_id)
        except Flashcard.DoesNotExist:
            current_card = flashcards.first() if flashcards.exists() else None
    else:
        current_card = flashcards.first() if flashcards.exists() else None
    
    # Render just the indicators section as HTML
    html = render_to_string('flashcards/partials/indicators.html', {
        'flashcards': flashcards,
        'current_card': current_card
    }, request=request)
    
    return JsonResponse({'html': html})

@login_required
def mark_reviewed_api(request):
    """API endpoint to mark a card as reviewed"""
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        card.num_revisions += 1
        card.save()
        
        return JsonResponse({
            'success': True,
            'num_revisions': card.num_revisions
        })
    
    return JsonResponse({'success': False}, status=400)

@login_required
def delete_flashcard_api(request):
    """API endpoint to delete a flashcard"""
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        
        # Get next and previous cards before deleting
        flashcards = Flashcard.objects.filter(user=request.user).order_by('num_revisions')
        flashcard_list = list(flashcards)
        
        try:
            current_index = flashcard_list.index(card)
            next_id = flashcards[current_index + 1].id if current_index < len(flashcards) - 1 else None
            prev_id = flashcards[current_index - 1].id if current_index > 0 else None
        except (ValueError, IndexError):
            next_id = None
            prev_id = None
            
        # Delete the card
        card.delete()
        
        # Count remaining cards
        remaining_count = Flashcard.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True,
            'count': remaining_count,
            'next_id': next_id,
            'prev_id': prev_id,
            'should_update_indicators': True
        })
    
    return JsonResponse({'success': False}, status=400)