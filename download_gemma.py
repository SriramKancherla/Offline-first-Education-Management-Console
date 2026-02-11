from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "google/gemma-2b-it"

print("Downloading Gemma model separately...")

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(model_name)

print("Download Complete!")
