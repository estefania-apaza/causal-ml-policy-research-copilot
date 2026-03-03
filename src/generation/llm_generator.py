import json
from openai import OpenAI

class Generator:
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.model_name = model_name
        self.client = OpenAI()

    def generate_answer(self, system_prompt: str, context: str, question: str, history: list = None, **kwargs) -> str:
        """
        Generates an answer using the provided system prompt template and conversation history.
        history: List of dictionaries with 'role' and 'content' keys.
        """
        # Accept any extra args gracefully via **kwargs
        if history is None:
            history = []
            
        try:
            formatted_system_prompt = system_prompt.format(context=context, question=question)
            
            messages = [{"role": "system", "content": formatted_system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": question})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        except KeyError: # Fallback if system prompt doesn't use placeholders
             messages = [{"role": "system", "content": system_prompt}]
             messages.extend(history)
             messages.append({"role": "user", "content": f"CONTEXT: {context}\n\nQUESTION: {question}"})
             
             response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3
            )
             return response.choices[0].message.content
             
    def generate_json_answer(self, system_prompt: str, context: str, question: str, history: list = None, **kwargs) -> dict:
        """
        Forces JSON output format based on system prompt instructions.
        history: List of dictionaries with 'role' and 'content' keys.
        """
        # Accept any extra args gracefully via **kwargs
        if history is None:
            history = []
            
        try:
            formatted_system_prompt = system_prompt.format(context=context, question=question)
            
            messages = [{"role": "system", "content": formatted_system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": question})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                response_format={ "type": "json_object" },
                messages=messages,
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "answer": "Failed to generate JSON output."}
