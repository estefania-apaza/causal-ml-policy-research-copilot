import json
from openai import OpenAI

client = OpenAI()

class Generator:
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.model_name = model_name

    def generate_answer(self, system_prompt: str, context: str, question: str) -> str:
        """
        Generates an answer using the provided system prompt template.
        The system prompt must contain {context} and {question} placeholders if they are formatted into the prompt.
        If they are not placeholders, we format the messages accordingly.
        """
        try:
            formatted_system_prompt = system_prompt.format(context=context, question=question)
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": formatted_system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except KeyError: # Fallback if system prompt doesn't use placeholders
             response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CONTEXT: {context}\n\nQUESTION: {question}"}
                ],
                temperature=0.3
            )
             return response.choices[0].message.content
             
    def generate_json_answer(self, system_prompt: str, context: str, question: str) -> dict:
        """
        Forces JSON output format based on system prompt instructions.
        """
        try:
            formatted_system_prompt = system_prompt.format(context=context, question=question)
            response = client.chat.completions.create(
                model=self.model_name,
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": formatted_system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "answer": "Failed to generate JSON output."}
