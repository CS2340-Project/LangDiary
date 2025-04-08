from django.shortcuts import render, redirect, get_object_or_404
from .models import Flashcard

def index(request):
    template_data = {'title': 'LangDiary - Flashcards'}
    flashcards = Flashcard.objects.all().order_by('num_revisions')

    # Handle card navigation
    card_id = request.GET.get('card_id')
    current_card_index = 0

    # Fix for empty queryset
    if not flashcards.exists():
        return render(request, 'flashcards/index.html', {
            'flashcards': [],
            'template_data': template_data,
        })

    # Select first card by default
    current_card = flashcards.first()

    if card_id:
        try:
            # Find the current card
            current_card = flashcards.get(id=card_id)
            # Find position in sequence
            flashcard_list = list(flashcards)
            current_card_index = flashcard_list.index(current_card)
        except (Flashcard.DoesNotExist, ValueError, IndexError):
            # Fall back to first card if error
            current_card = flashcards.first()
            current_card_index = 0

    # Get previous and next card IDs
    prev_card_id = flashcards[current_card_index - 1].id if current_card_index > 0 else None
    next_card_id = flashcards[current_card_index + 1].id if current_card_index < len(flashcards) - 1 else None

    # Handle edit mode
    edit_card = None
    if request.GET.get('action') == 'edit' and request.GET.get('id'):
        edit_card = get_object_or_404(Flashcard, id=request.GET.get('id'))

    return render(request, 'flashcards/index.html', {
        'flashcards': flashcards,
        'current_card': current_card,
        'template_data': template_data,
        'prev_card_id': prev_card_id,
        'next_card_id': next_card_id,
        'edit_card': edit_card,
    })

def create_flashcard(request):
    if request.method == 'POST':
        front_text = request.POST.get('front_text')
        back_text = request.POST.get('back_text')
        Flashcard.objects.create(front_text=front_text, back_text=back_text)
    return redirect('flashcards.index')

def update_flashcard(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id)
        card.front_text = request.POST.get('front_text')
        card.back_text = request.POST.get('back_text')
        card.save()
    return redirect('flashcards.index')

def delete_flashcard(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id)
        card.delete()
    return redirect('flashcards.index')

def mark_reviewed(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id)
        card.num_revisions += 1
        card.save()
    return redirect('flashcards.index')