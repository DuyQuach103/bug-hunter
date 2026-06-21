import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Attempt to configure the Gemini client
# We support google-genai (new SDK) as primary, and google-generativeai (legacy SDK) as fallback
GEMINI_CLIENT = None
LEGACY_GENAI = False

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

try:
    from google import genai
    from google.genai import types
    if api_key:
        GEMINI_CLIENT = genai.Client(api_key=api_key)
except (ImportError, ValueError):
    pass

# Setup legacy fallback if client is not configured
try:
    if not GEMINI_CLIENT:
        import google.generativeai as legacy_genai
        if api_key:
            legacy_genai.configure(api_key=api_key)
        LEGACY_GENAI = True
except ImportError:
    pass


class JudgeEvaluation(BaseModel):
    accuracy: int = Field(description="Accuracy score (1-10): Did it find all bugs?")
    correctness: int = Field(description="Correctness score (1-10): Are the fixes correct?")
    completeness: int = Field(description="Completeness score (1-10): Did it miss anything?")
    helpfulness: int = Field(description="Helpfulness score (1-10): Are recommendations useful?")
    justification: str = Field(description="Detailed rationale and justification for each score")


class LLMJudge:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key and not GEMINI_CLIENT:
            print("Warning: Gemini API key is not set. Evaluations may fail.")

    def evaluate_analysis(self, original_code: str, report: dict) -> dict:
        """
        Evaluates Bug Hunter's analysis report against the original code using Gemini.
        Returns a dictionary with accuracy, correctness, completeness, helpfulness, overall_score, and justification.
        """
        # Format the report nicely as JSON/text for the prompt
        report_str = json.dumps(report, indent=2)

        prompt = f"""
        You are an expert code reviewer evaluating another AI's code analysis.

        Given:
        1. The original code
        2. The AI's analysis report

        Score the analysis on:
        - Accuracy (1-10): Did it find all bugs?
        - Correctness (1-10): Are the fixes correct?
        - Completeness (1-10): Did it miss anything?
        - Helpfulness (1-10): Are recommendations useful?

        Original Code:
        ```python
        {original_code}
        ```

        AI's Analysis Report:
        {report_str}

        Return your evaluation conforming strictly to the requested JSON schema.
        """

        models_to_try = ['gemini-2.5-flash']
        last_error = None

        if not LEGACY_GENAI:
            client = GEMINI_CLIENT or genai.Client(api_key=self.api_key)
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=JudgeEvaluation,
                            temperature=0.1,
                        ),
                    )
                    eval_data = json.loads(response.text)
                    # Calculate overall score as average
                    scores = [eval_data['accuracy'], eval_data['correctness'], eval_data['completeness'], eval_data['helpfulness']]
                    eval_data['overall_score'] = round(sum(scores) / len(scores), 2)
                    return eval_data
                except Exception as e:
                    print(f"Judge evaluation failed with model {model_name}: {e}")
                    if last_error is None or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        last_error = e
            raise last_error
        else:
            for model_name in models_to_try:
                try:
                    model = legacy_genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            "response_mime_type": "application/json",
                            "response_schema": JudgeEvaluation if hasattr(legacy_genai, 'protos') else None
                        }
                    )
                    eval_data = json.loads(response.text)
                    scores = [eval_data['accuracy'], eval_data['correctness'], eval_data['completeness'], eval_data['helpfulness']]
                    eval_data['overall_score'] = round(sum(scores) / len(scores), 2)
                    return eval_data
                except Exception as e:
                    print(f"Legacy judge evaluation failed with model {model_name}: {e}")
                    if last_error is None or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        last_error = e
            raise last_error


# Example usage
if __name__ == "__main__":
    judge = LLMJudge()
    
    # Test stub
    test_code = "def add(a, b):\n    return a + b"
    test_report = {
        "syntax_errors": [],
        "logic_errors": [],
        "performance_issues": [],
        "security_issues": [],
        "strengths": ["Clean function", "Correct implementation"],
        "recommendations": [],
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "quality_score": 10
    }
    
    try:
        result = judge.evaluate_analysis(test_code, test_report)
        print("Test Judge Output:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("Failed to run example evaluation:", e)
