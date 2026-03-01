import os
import sys

# Add parent directory to path to allow importing src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from src.rag_pipeline import RAGPipeline

def evaluate_strategies():
    """Evaluate all 4 strategies on the set of questions."""
    print("Initializing RAG Pipeline for evaluation...")
    rag = RAGPipeline()
    
    with open("eval/questions.json", "r") as f:
        questions = json.load(f)
        
    strategies = [
        "v1_delimiters",
        "v2_json_output",
        "v3_few_shot",
        "v4_chain_of_thought"
    ]
    
    results = {}
    
    for q in questions:
        print(f"\n--- Question: {q['question']} ---")
        q_results = {}
        for strategy in strategies:
            print(f"Testing {strategy}...")
            try:
                answer = rag.answer_question(q['question'], strategy)
                q_results[strategy] = answer
            except Exception as e:
                q_results[strategy] = f"Error: {e}"
        results[q['id']] = {
            "question": q['question'],
            "expected_keywords": q['expected_keywords'],
            "answers": q_results
        }
        
    with open("eval/results/eval_results.json", "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print("\nEvaluation complete. Results saved to eval/results/eval_results.json.")

if __name__ == "__main__":
    if not os.path.exists("eval/results"):
        os.makedirs("eval/results")
    evaluate_strategies()
