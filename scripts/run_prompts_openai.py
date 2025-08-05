#!/usr/bin/env python3
"""
OpenAI GPT-4 API client for prompt evaluation.
Runs prompts against OpenAI's GPT-4 model and tracks performance metrics.
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
from utils import (
    load_prompts, save_results, calculate_tokens_cost, 
    format_response_data, log_error, calculate_response_stats
)

# Load environment variables from .env file
load_dotenv()

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def send_prompt(self, prompt_content: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Send a single prompt to OpenAI API and return response with metrics."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt_content}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Extract response data
            response_text = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            
            # Calculate cost
            cost = calculate_tokens_cost(input_tokens, output_tokens, self.model)
            
            return {
                "success": True,
                "response": response_text,
                "latency": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost
            }
            
        except Exception as e:
            end_time = time.time()
            latency = end_time - start_time
            
            return {
                "success": False,
                "error": str(e),
                "latency": latency,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0
            }

def run_prompt_category(client: OpenAIClient, prompts: List[Dict], category: str) -> List[Dict[str, Any]]:
    """Run all prompts in a category and collect results."""
    results = []
    
    print(f"Running {len(prompts)} prompts for category: {category}")
    
    for i, prompt in enumerate(prompts, 1):
        print(f"  Processing prompt {i}/{len(prompts)}: {prompt['id']}")
        
        # Send prompt to API
        api_result = client.send_prompt(prompt['content'])
        
        if api_result['success']:
            # Format successful response
            result = format_response_data(
                prompt_id=prompt['id'],
                response=api_result['response'],
                latency=api_result['latency'],
                input_tokens=api_result['input_tokens'],
                output_tokens=api_result['output_tokens'],
                cost=api_result['cost'],
                model=client.model
            )
            result['category'] = category
            results.append(result)
            
            print(f"    ✓ Success - {api_result['latency']:.2f}s, ${api_result['cost']:.4f}")
            
        else:
            # Log error and create error result
            error_msg = f"Failed to process prompt {prompt['id']}: {api_result['error']}"
            log_error(error_msg, prompt['id'])
            
            result = format_response_data(
                prompt_id=prompt['id'],
                response=f"ERROR: {api_result['error']}",
                latency=api_result['latency'],
                model=client.model
            )
            result['category'] = category
            result['error'] = True
            results.append(result)
            
            print(f"    ✗ Failed - {api_result['error']}")
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Run prompts against OpenAI GPT-4")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"), 
                       help="OpenAI API key (can be set via OPENAI_API_KEY env var)")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4"), 
                       help=f"OpenAI model to use (default: {os.getenv('OPENAI_MODEL', 'gpt-4')})")
    parser.add_argument("--categories", nargs="+", 
                       choices=["instruction", "reasoning", "creative", "coding"], 
                       default=["instruction", "reasoning", "creative", "coding"],
                       help="Categories to run (default: all)")
    parser.add_argument("--output-dir", default=os.getenv("RESULTS_DIR", "../results"), 
                       help=f"Output directory for results (default: {os.getenv('RESULTS_DIR', '../results')})")
    
    args = parser.parse_args()
    
    # Validate API key
    if not args.api_key:
        print("❌ OpenAI API key is required!")
        print("Set it via environment variable: export OPENAI_API_KEY=your_key_here")
        print("Or use --api-key argument")
        sys.exit(1)
    
    # Initialize client
    client = OpenAIClient(args.api_key, args.model)
    
    all_results = []
    
    # Process each category
    for category in args.categories:
        print(f"\n{'='*50}")
        print(f"Processing category: {category.upper()}")
        print(f"{'='*50}")
        
        # Load prompts
        prompt_file = f"../data/prompts/{category}.json"
        if not os.path.exists(prompt_file):
            print(f"Warning: Prompt file not found: {prompt_file}")
            continue
        
        prompts = load_prompts(prompt_file)
        
        # Run prompts
        category_results = run_prompt_category(client, prompts, category)
        all_results.extend(category_results)
    
    # Save results
    if all_results:
        output_file = os.path.join(args.output_dir, "openai_outputs.json")
        save_results(all_results, output_file)
        
        # Calculate and display statistics
        stats = calculate_response_stats(all_results)
        
        print(f"\n{'='*50}")
        print("SUMMARY STATISTICS")
        print(f"{'='*50}")
        print(f"Total responses: {stats['total_responses']}")
        print(f"Average latency: {stats['avg_latency_seconds']}s")
        print(f"Total tokens: {stats['total_tokens']}")
        print(f"Total cost: ${stats['total_cost_usd']}")
        print(f"Average response length: {stats['avg_response_length']} characters")
        
        print(f"\nResults saved to: {output_file}")
    else:
        print("No results to save.")

if __name__ == "__main__":
    main()