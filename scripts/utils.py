import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any

def load_prompts(file_path: str) -> List[Dict[str, Any]]:
    """Load prompts from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_results(results: List[Dict[str, Any]], file_path: str) -> None:
    """Save results to a JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def calculate_tokens_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4") -> float:
    """Calculate cost based on token usage for OpenAI models."""
    # GPT-4 pricing (as of 2024)
    pricing = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015}
    }
    
    if model not in pricing:
        model = "gpt-4"  # default fallback
    
    input_cost = (input_tokens / 1000) * pricing[model]["input"]
    output_cost = (output_tokens / 1000) * pricing[model]["output"]
    
    return input_cost + output_cost

def measure_time(func):
    """Decorator to measure execution time of functions."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper

def format_response_data(prompt_id: str, response: str, latency: float, 
                        input_tokens: int = 0, output_tokens: int = 0, 
                        cost: float = 0.0, model: str = "unknown") -> Dict[str, Any]:
    """Format response data into a standardized structure."""
    return {
        "prompt_id": prompt_id,
        "model": model,
        "response": response,
        "latency_seconds": round(latency, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(cost, 6),
        "timestamp": datetime.now().isoformat(),
        "response_length": len(response),
        "words_count": len(response.split())
    }

def log_error(error_msg: str, prompt_id: str = None, file_path: str = "error.log") -> None:
    """Log errors to a file."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] Error"
    if prompt_id:
        log_entry += f" (Prompt: {prompt_id})"
    log_entry += f": {error_msg}\n"
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def calculate_response_stats(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate statistics for a set of responses."""
    if not responses:
        return {}
    
    total_latency = sum(r.get('latency_seconds', 0) for r in responses)
    total_tokens = sum(r.get('total_tokens', 0) for r in responses)
    total_cost = sum(r.get('cost_usd', 0) for r in responses)
    response_lengths = [r.get('response_length', 0) for r in responses]
    
    return {
        "total_responses": len(responses),
        "avg_latency_seconds": round(total_latency / len(responses), 3),
        "total_tokens": total_tokens,
        "avg_tokens_per_response": round(total_tokens / len(responses), 1),
        "total_cost_usd": round(total_cost, 4),
        "avg_response_length": round(sum(response_lengths) / len(responses), 1),
        "min_response_length": min(response_lengths),
        "max_response_length": max(response_lengths)
    }

def create_comparison_summary(openai_results: List[Dict], local_results: List[Dict]) -> Dict[str, Any]:
    """Create a summary comparison between OpenAI and local model results."""
    openai_stats = calculate_response_stats(openai_results)
    local_stats = calculate_response_stats(local_results)
    
    return {
        "openai_model": openai_stats,
        "local_model": local_stats,
        "comparison": {
            "latency_ratio": round(local_stats.get('avg_latency_seconds', 0) / max(openai_stats.get('avg_latency_seconds', 1), 0.001), 2),
            "token_efficiency": round(local_stats.get('avg_tokens_per_response', 0) / max(openai_stats.get('avg_tokens_per_response', 1), 1), 2),
            "cost_savings": openai_stats.get('total_cost_usd', 0),
            "response_length_ratio": round(local_stats.get('avg_response_length', 0) / max(openai_stats.get('avg_response_length', 1), 1), 2)
        }
    }