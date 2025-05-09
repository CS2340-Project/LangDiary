# LangDiary

LangDiary is a web application that provides a path to immersive language learning. Rather than drilling flashcards or playing games like Duolingo to learn a target language, users will be given a platform to add immersion and input into their language learning journey. After logging in for the first time, users can select a target language like English, Spanish, or French to learn. Users can input their location to find local areas and events that can immerse them in the culture that speaks that language. For example, if a user wants to learn French and they give their location, and be given a map of French speaking or inspired areas/events in their community e.g. a French style cafe, French speaking conferences happening nearby, etc.

LangDiary’s goal is to help users learn their target language. It can create a weekly calendar plan of exercises for users to practice and record in their lang diary such as asking them to write a short story in their target language about a specific prompt, write emails style entries, and more. LangDiary will also provide a brief overview of grammatical rules of the target language in the form of short daily videos users can watch when they log in. A crucial part of LangDiary is its LLM powered feedback. Users can get weekly feedback on an exercise tailored to their skill level and needs. LangDiary will also provide the traditional language learning website experience of flashcard style practice so that users can memorize words and phrases

This solution will allow users to create an account, outline their language goals and select a target language. Each user can manage their lang diary by creating and viewing responses to exercises, flashcards, and viewing their LangLocale which consists of local language/ culture related areas. Users may also review personalized feedback on their exercises as well as watch a set of daily videos to introduce / reinforce grammar concepts.

## Running
Create virtual environment, if not created by default to avoid flooding your device with packages.
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
The features that require API keys (email confirmation and Google Places API) won't work.
