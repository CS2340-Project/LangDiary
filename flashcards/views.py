from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Flashcard

@login_required
def index(request):
    template_data = {'title': 'LangDiary - Flashcards'}
    flashcards = Flashcard.objects.filter(user=request.user).order_by('num_revisions')

    card_id = request.GET.get('card_id')
    current_card_index = 0

    if not flashcards.exists():
        return render(request, 'flashcards/index.html', {
            'flashcards': [],
            'template_data': template_data,
        })

    current_card = flashcards.first()

    if card_id:
        try:
            current_card = flashcards.get(id=card_id)
            flashcard_list = list(flashcards)
            current_card_index = flashcard_list.index(current_card)
        except (Flashcard.DoesNotExist, ValueError, IndexError):
            current_card = flashcards.first()
            current_card_index = 0

    prev_card_id = flashcards[current_card_index - 1].id if current_card_index > 0 else None
    next_card_id = flashcards[current_card_index + 1].id if current_card_index < len(flashcards) - 1 else None

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

@login_required
def create_flashcard(request):
    if request.method == 'POST':
        front_text = request.POST.get('front_text')
        back_text = request.POST.get('back_text')
        Flashcard.objects.create(
            user=request.user,
            front_text=front_text,
            back_text=back_text
        )
    return redirect('flashcards.index')

@login_required
def update_flashcard(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        card.front_text = request.POST.get('front_text')
        card.back_text = request.POST.get('back_text')
        card.save()
    return redirect('flashcards.index')

@login_required
def delete_flashcard(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        card.delete()
    return redirect('flashcards.index')

@login_required
def mark_reviewed(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        card.num_revisions += 1
        card.save()
    return redirect('flashcards.index')