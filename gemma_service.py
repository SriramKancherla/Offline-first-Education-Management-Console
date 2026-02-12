from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "google/gemma-2b-it"

print("🔄 Loading Gemma Model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16
)

print("✅ Gemma Model Loaded Successfully!")


def build_prompt(text_chunk, difficulty, mode):
    """
    Builds DIFFERENT prompts for worksheet vs assessment
    and forces use of ONLY knowledge base content.
    """

    base = f"""
You are an educational content generator.

Use ONLY the information provided below.
Do NOT add outside knowledge.

CONTENT:
{text_chunk}

DIFFICULTY LEVEL: {difficulty}
"""

    if mode == "worksheet":
        prompt = base + """

TASK: Create a STUDENT WORKSHEET.

Generate:

1) 5 Multiple Choice Questions
2) 3 Short Answer Questions
3) 2 Long Answer Questions

Finally provide:

ANSWER KEY with clear explanations.

Do not invent facts.
Only use the provided content.
"""

    else:
        prompt = base + """

TASK: Create a FORMAL ASSESSMENT.

Generate:

SECTION A – MCQs
- 10 Multiple Choice Questions

SECTION B – Short Answer
- 5 Short Answer Questions

SECTION C – Long Answer
- 3 Long Answer Questions

Provide:

- Clear marking scheme
- Rubrics
- Answer key

STRICT RULE:
Use ONLY information from the given content.
"""

    return prompt


def generate_with_gemma(prompt):

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=700,
        temperature=0.6,
        top_p=0.9,
        do_sample=True
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return result
