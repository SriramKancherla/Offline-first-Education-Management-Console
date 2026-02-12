from llama_cpp import Llama
import os

# Configuration
MODEL_PATH = "model/gemma-2b-it-q4_k_m.gguf"
CONTEXT_SIZE = 2048


class LLMService:
    def __init__(self):
        self.llm = None

        if os.path.exists(MODEL_PATH):
            print(f"Loading LLM from {MODEL_PATH}...")

            try:
                self.llm = Llama(
                    model_path=MODEL_PATH,
                    n_ctx=CONTEXT_SIZE,
                    n_threads=4
                )

                print("LLM loaded successfully.")

            except Exception as e:
                print(f"Failed to load LLM: {e}")

        else:
            print(f"Warning: LLM model not found at {MODEL_PATH}. Using mock response.")

    def generate(self, prompt: str, max_tokens: int = 700) -> str:

        if not self.llm:
            return f"[MODEL NOT LOADED] Missing model at: {MODEL_PATH}"

        try:
            output = self.llm(
                f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n",
                max_tokens=max_tokens,
                stop=["<end_of_turn>", "User:", "System:"],
                echo=False
            )

            return output["choices"][0]["text"].strip()

        except Exception as e:
            print(f"Generation error: {e}")
            return f"Generation failed: {str(e)}"


# Singleton instance
llm_service = LLMService()


# ======================================================
# REQUIRED FUNCTIONS FOR AI SERVER
# ======================================================

def build_prompt(text_chunk, difficulty, mode):

    base = f"""
You are an educational content generator.

Use ONLY the information provided below.
Do NOT add outside knowledge.

CONTENT:
{text_chunk}

DIFFICULTY LEVEL: {difficulty}
"""

    if mode == "worksheet":

        return base + """

TASK: Create a STUDENT WORKSHEET.

Generate:
- 5 Multiple Choice Questions
- 3 Short Answer Questions
- 2 Long Answer Questions

Provide ANSWER KEY.

STRICT RULE:
Use ONLY provided content.
"""

    else:

        return base + """

TASK: Create a FORMAL ASSESSMENT.

SECTION A – 10 MCQs
SECTION B – 5 Short Answer
SECTION C – 3 Long Answer

Provide:
- marking scheme
- rubric
- answer key

STRICT RULE:
Use ONLY provided content.
"""


def generate_with_gemma(prompt):

    return llm_service.generate(prompt)
