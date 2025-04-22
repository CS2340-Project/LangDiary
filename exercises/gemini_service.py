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
            You are a strict feedback generator for a {level}-level learner writing in {language}. Your job is to return **only** inline corrections to the learner's writing, followed by a score.

            The learner responded to the prompt "{exercise_prompt}" with this submission:

            "{user_submission}"

            Your response format must be exactly:

            [Corrected and annotated version using ~~strikethrough~~ for mistakes and (brief explanations) directly after each]

            ---

            [score]/100

            Instructions (follow strictly):
            - DO NOT reprint the learner’s original submission.
            - DO NOT provide greetings, summaries, or general comments.
            - DO NOT explain anything outside the rewritten sentence.
            - Only use inline annotations: ~~error~~ (explanation).
            -Preseve mistakes, annotate after them.
            - DO NOT say anything at the start like "Corrected and annotated version using ~~strikethrough~~ for mistakes and (brief explanations) directly after each".
            - GET DIRECTLY INTO THE CORRECTED MESSAGE
            - Score must be on its own line, exactly like this:

            ---

            84/100
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
                {"score": score_line}
            ]
        except Exception as e:
            print(f"Error parsing feedback: {str(e)}")
            return [{"text": response_text.strip(), "score": "N/A"}]
        
