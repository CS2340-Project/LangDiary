# flashcards/gemini_service.py
import google.generativeai as genai
import os
from typing import List, Dict

class GeminiService:
    """Service to interact with Gemini API for feedback generation"""
    
    def __init__(self):
        """Initialize the Gemini API with the API key from settings"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def generate_feedback(self, language: str, level: str, exercise_prompt: str, user_submission: str) -> str:
        gemini_prompt = self._create_feedback_prompt(language, level, exercise_prompt, user_submission)
        
        try:
            response = self.model.generate_content(gemini_prompt)
            return self._parse_feedback_response(response.text)
        except Exception as e:
            # Log the error and return empty list
            print(f"Error generating feedback: {str(e)}")
            return user_submission
    
    def _create_feedback_prompt(self, language: str, level: str, exercise_prompt: str, user_submission: str) -> str:
        return f"""
        You are a strict language feedback generator for a {level}-level learner writing in {language}. The learner responded to the prompt:

        "{exercise_prompt}"

        Their submission was:

        "{user_submission}"

        Your task is to provide inline corrections directly in their submission using this exact format:

        - Use ~~strikethrough~~ to mark any mistakes.
        - Immediately follow each mistake with a brief explanation in parentheses.
        - Do NOT delete or rephrase the learner’s words — preserve their original phrasing and annotate errors inline.
        - Do NOT summarize or rephrase the submission.
        - Do NOT add greetings, introductions, or explanations outside the annotated text.
        - DO NOT say anything like “Corrected version:” or describe your format.
        - DO NOT add comments or reflections about the learner’s level or effort.

        Return only:

        [Corrected and annotated sentence with inline edits]

        ---

        [Numeric score from 0 to 100]

        Your score should reflect the accuracy of the learner's writing, considering grammar, vocabulary, spelling, syntax, and fluency — adjusted to the learner's level.

        Examples of formatting:
        Je ~~suis~~ *(Use "m'appelle" for introductions)* Marie.
        ---
        78/100
        """
        
    
    def _parse_feedback_response(self, response_text: str) -> List[Dict[str, str]]:
        try:
            if "---" not in response_text:
                return [{"text": response_text.strip(), "score": "N/A"}]
            
            parts = response_text.split("---")
            feedback_text = parts[0].strip()
            score_line = parts[1].strip()

            return [
                {"text": feedback_text},
                {"score": score_line[0:2]}
            ]
        except Exception as e:
            print(f"Error parsing feedback: {str(e)}")
            return [{"text": response_text.strip(), "score": "N/A"}]
        
