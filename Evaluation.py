import openai

openai.api_key = "Blocked API key for presentation purposes"


def evaluate_sentence(sentence):
    system_prompt = (
        "You are a strict language evaluator. Provide a numeric rating and brief analysis."
    )

    user_prompt = f"""
You are tasked with evaluating a summary of a Youtube Video comment section. You must evaluate the summary on four metrics. Clarity, coherence, relevance, and substance. Give a score (1/5) on each of the metrics and give an explanation of how each score could be improved. The example summary will be given below.
"{sentence}"
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or gpt-4 if you have access
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,  # For more consistent output
    )

    return response["choices"][0]["message"]["content"].strip()


# Example usage
test_sentence = "The presentation is expandable, and I’m thrilled to see it lapsed focus."
evaluation = evaluate_sentence(test_sentence)
print(evaluation)

res_text = '''
Sentence: "The presentation is expandable, and I’m thrilled to see it lapsed focus."
            
Evaluation:
Grammar/Spelling: 6/10
Rationale: There are no spelling errors, but the grammar is off. The phrase "see it lapsed focus" is grammatically incorrect. "Lapsed" is not used properly here.

Fluency/Readability: 5/10
Rationale: The sentence begins clearly but becomes confusing in the second half. The reader struggles to understand what “see it lapsed focus” means, disrupting readability.

Logical Consistency: 3/10
Rationale: The sentence does not make logical sense as written. It's unclear what is meant by “see it lapsed focus.” The idea seems self-contradictory or incomplete.

Overall Average Score: 4.7 / 10
'''

print(res_text)

