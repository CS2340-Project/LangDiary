# flashcards/profile_integration.py

def get_user_language_preferences(user):
    """
    Get language learning preferences from the user's profile.
    Returns a dictionary with default values for the flashcard generator form.
    
    Args:
        user: The user object to get preferences for
        
    Returns:
        dict: Default values for the generator form
    """
    defaults = {
        'language': 'spanish',  # Default to Spanish if no preference
        'level': 'beginner',    # Default to beginner if no preference
        'topic': 'greetings',   # Default to greetings
        'count': 5              # Default to 5 cards
    }
    
    # Try to get the user's profile
    try:
        profile = user.profile  # Assuming the profile is directly accessible via user.profile
        
        # Map the language_learning field to our language choices
        if hasattr(profile, 'language_learning'):
            language = profile.language_learning.lower()
            if language in ['spanish', 'french', 'german']:
                defaults['language'] = language
        
        # Map the language_level field to our level choices
        if hasattr(profile, 'language_level'):
            level = profile.language_level.lower()
            if level in ['beginner', 'intermediate', 'advanced']:
                defaults['level'] = level
                
        # If the user has learning_goals, use the first one as a custom topic
        if hasattr(profile, 'learning_goals') and profile.learning_goals:
            goals = profile.learning_goals
            if goals:
                defaults['topic'] = 'custom'
                defaults['custom_topic'] = goals[:100]  # Limit to 100 chars
                
    except (AttributeError, Exception):
        # If there's any error, just use the defaults
        pass
        
    return defaults