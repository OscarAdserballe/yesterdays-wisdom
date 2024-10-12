import os

root_dir = "/Users/oscarjuliusadserballe/cli_scripts/prompts"


filepaths = {
    "code" : "coding_prompt.txt",
    "study" : "study_prompt.txt",
    "math" : "math_prompt.txt",
    "write" : "writing_prompt.txt",
    "summary" : "summary_prompt.txt",
}

PROMPTS = {
    "default" : """
Answer questions concisely. Format as raw text, and be cognizant that output will be displayed in a shell, so no HTML, newlines etc.
"""
}

for key, value in filepaths.items():
    with open(os.path.join(root_dir, value), "r") as f:
        PROMPTS[key] = f.read()
