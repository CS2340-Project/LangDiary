from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Flashcard

def index(request):
    flashcards = Flashcard.objects.all().order_by('num_revisions')
    return render(request, 'flashcards/index.html', {'flashcards': flashcards})


# TODO: make a proper business logic for creating/deleting/editing flashcards
# TODO: order flashcards by num_revisions
def create_flashcard(request):
    if request.method == 'POST':
        front_text = request.POST.get('front_text')
        back_text = request.POST.get('back_text')
        Flashcard.objects.create(front_text=front_text, back_text=back_text)
        return redirect('index')
    return redirect('index')

def update_flashcard(request, card_id):
    card = get_object_or_404(Flashcard, id=card_id)
    if request.method == 'POST':
        card.front_text = request.POST.get('front_text')
        card.back_text = request.POST.get('back_text')
        card.save()
        return redirect('index')
    return redirect('index')

def delete_flashcard(request, card_id):
    card = get_object_or_404(Flashcard, id=card_id)
    if request.method == 'POST':
        card.delete()
    return redirect('index')

def mark_reviewed(request, card_id):
    card = get_object_or_404(Flashcard, id=card_id)
    if request.method == 'POST':
        card.num_revisions += 1
        card.save()
        return JsonResponse({'success': True, 'revisions': card.num_revisions})
    return JsonResponse({'success': False})