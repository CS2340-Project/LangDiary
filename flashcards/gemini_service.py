# flashcards/gemini_service.py
import google.generativeai as genai
import os
from typing import List, Dict

class GeminiService:
    """Service to interact with Gemini API for flashcard generation"""
    
    def __init__(self):
        """Initialize the Gemini API with the API key from settings"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def generate_flashcards(self, language: str, level: str, topic: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Generate flashcards for language learning
        
        Args:
            language: Target language to learn
            level: Proficiency level (beginner, intermediate, advanced)
            topic: Topic for flashcards
            count: Number of flashcards to generate
            
        Returns:
            List of dictionaries with front_text and back_text keys
        """
        prompt = self._create_flashcard_prompt(language, level, topic, count)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_flashcards_response(response.text)
        except Exception as e:
            # Log the error and return empty list
            print(f"Error generating flashcards: {str(e)}")
            return []
    
    def _create_flashcard_prompt(self, language: str, level: str, topic: str, count: int) -> str:
        """Create a well-structured prompt for Gemini"""
        return f"""
        I need {count} flashcards to help me learn {language} at a {level} level about the topic: {topic}.

        For each flashcard:
        - If I'm a beginner, the front should be in English and the back should be in {language}
        - If I'm intermediate or advanced, the front should be in {language} and the back should be in English
        - Include relevant grammar notes or pronunciation tips on the back when applicable
        
        Please format your response exactly like this, with one flashcard per line:
        
        FRONT: [front text]
        BACK: [back text]
        ---
        FRONT: [front text]
        BACK: [back text]
        ---
        
        Make the flashcards contextually useful for real-world situations.
        """
    
    def _parse_flashcards_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse the response from Gemini into a list of flashcard dictionaries"""
        flashcards = []
        
        # Split the response by the separator
        cards_raw = response_text.split("---")
        
        for card_text in cards_raw:
            if not card_text.strip():
                continue
                
            lines = card_text.strip().split("\n")
            front_text = ""
            back_text = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("FRONT:"):
                    front_text = line[6:].strip()
                elif line.startswith("BACK:"):
                    back_text = line[5:].strip()
            
            if front_text and back_text:
                flashcards.append({
                    "front_text": front_text,
                    "back_text": back_text
                })
        
        return flashcards