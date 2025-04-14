from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Flashcard
from .forms import FlashcardGeneratorForm
from .gemini_service import GeminiService
from .profile_integration import get_user_language_preferences

@login_required
def index(request):
    template_data = {'title': 'LangDiary - Flashcards'}
    flashcards = Flashcard.objects.filter(user=request.user).order_by('num_revisions')

    # Initialize the generator form
    generator_form = FlashcardGeneratorForm()
    
    # Check if we need to show the generator modal
    show_generator = request.GET.get('generator') == 'show'
    is_generating = False

    card_id = request.GET.get('card_id')
    current_card_index = 0

    if not flashcards.exists():
        return render(request, 'flashcards/index.html', {
            'flashcards': [],
            'template_data': template_data,
            'form': generator_form,
            'show_generator': show_generator,
            'is_generating': is_generating,
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
        'form': generator_form,
        'show_generator': show_generator,
        'is_generating': is_generating,
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

@login_required
def generate_flashcards(request):
    """Generate flashcards using Gemini API"""
    if request.method == 'POST':
        form = FlashcardGeneratorForm(request.POST)
        
        if form.is_valid():
            # Get form data
            language = form.cleaned_data['language']
            level = form.cleaned_data['level']
            topic = form.cleaned_data['topic']
            count = int(form.cleaned_data['count'])
            
            # If custom topic is selected, use the custom topic text
            if topic == 'custom':
                topic = form.cleaned_data['custom_topic']
                if not topic:
                    messages.error(request, "Please enter a custom topic")
                    return redirect('flashcards.index', generator='show')
            
            try:
                # Create service and generate flashcards
                gemini = GeminiService()
                generated_cards = gemini.generate_flashcards(language, level, topic, count)
                
                # Create flashcards in the database
                created_count = 0
                for card in generated_cards:
                    Flashcard.objects.create(
                        user=request.user,
                        front_text=card['front_text'],
                        back_text=card['back_text']
                    )
                    created_count += 1
                
                if created_count > 0:
                    messages.success(request, f"Successfully generated {created_count} flashcards for {language} on {topic}")
                else:
                    messages.warning(request, "No flashcards were generated. Please try again.")
                
            except Exception as e:
                messages.error(request, f"Error generating flashcards: {str(e)}")
        
        else:
            # Form is invalid
            messages.error(request, "Please correct the errors in the form")
    
    return redirect('flashcards.index')