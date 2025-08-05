#!/usr/bin/env python3
"""
Local LM Studio API client for prompt evaluation.
Runs prompts against local GPT-OSS-20B model via LM Studio and tracks performance metrics.
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
    load_prompts, save_results, format_response_data, 
    log_error, calculate_response_stats
)

# Load environment variables from .env file
load_dotenv()

class LocalLMClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1234", model_name: str = "gpt-oss-20b"):
        self.base_url = f"{base_url}/v1/chat/completions"
        self.model_name = model_name
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> bool:
        """Test if LM Studio is running and accessible."""
        try:
            # Try to reach the base URL or a health endpoint
            test_url = self.base_url.replace('/v1/chat/completions', '/v1/models')
            response = requests.get(test_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_prompt(self, prompt_content: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Send a single prompt to local LM Studio API and return response with metrics."""
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt_content}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=120  # Local models might be slower
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Extract response data
            if 'choices' in data and len(data['choices']) > 0:
                response_text = data['choices'][0]['message']['content']
            else:
                raise Exception("No response choices found in API response")
            
            # Try to get token usage if available (LM Studio may or may not provide this)
            usage = data.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            
            return {
                "success": True,
                "response": response_text,
                "latency": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": 0.0  # Local inference has no API cost
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

def run_prompt_category(client: LocalLMClient, prompts: List[Dict], category: str) -> List[Dict[str, Any]]:
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
                model=client.model_name
            )
            result['category'] = category
            results.append(result)
            
            tokens_info = ""
            if api_result['input_tokens'] > 0 or api_result['output_tokens'] > 0:
                tokens_info = f", {api_result['input_tokens']+api_result['output_tokens']} tokens"
            
            print(f"    ✓ Success - {api_result['latency']:.2f}s{tokens_info}")
            
        else:
            # Log error and create error result
            error_msg = f"Failed to process prompt {prompt['id']}: {api_result['error']}"
            log_error(error_msg, prompt['id'])
            
            result = format_response_data(
                prompt_id=prompt['id'],
                response=f"ERROR: {api_result['error']}",
                latency=api_result['latency'],
                model=client.model_name
            )
            result['category'] = category
            result['error'] = True
            results.append(result)
            
            print(f"    ✗ Failed - {api_result['error']}")
        
        # Small delay between requests to avoid overwhelming the local server
        time.sleep(0.1)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Run prompts against local LM Studio model")
    parser.add_argument("--url", default=os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234"), 
                       help=f"LM Studio base URL (default: {os.getenv('LM_STUDIO_URL', 'http://127.0.0.1:1234')})")
    parser.add_argument("--model", default=os.getenv("LOCAL_MODEL_NAME", "gpt-oss-20b"), 
                       help=f"Model name (default: {os.getenv('LOCAL_MODEL_NAME', 'gpt-oss-20b')})")
    parser.add_argument("--categories", nargs="+", 
                       choices=["instruction", "reasoning", "creative", "coding"], 
                       default=["instruction", "reasoning", "creative", "coding"],
                       help="Categories to run (default: all)")
    parser.add_argument("--output-dir", default=os.getenv("RESULTS_DIR", "../results"), 
                       help=f"Output directory for results (default: {os.getenv('RESULTS_DIR', '../results')})")
    
    args = parser.parse_args()
    
    # Initialize client
    client = LocalLMClient(args.url, args.model)
    
    # Test connection
    print("Testing connection to LM Studio...")
    if not client.test_connection():
        print("❌ Failed to connect to LM Studio!")
        print("Make sure LM Studio is running and the API server is started.")
        print(f"Expected URL: {args.url}")
        print("\nTo start LM Studio API server:")
        print("1. Open LM Studio")
        print("2. Go to 'Local Server' tab")
        print("3. Load your GPT-OSS-20B model")
        print("4. Click 'Start Server'")
        sys.exit(1)
    
    print("✅ Connection successful!")
    
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
        output_file = os.path.join(args.output_dir, "local_outputs.json")
        save_results(all_results, output_file)
        
        # Calculate and display statistics
        stats = calculate_response_stats(all_results)
        
        print(f"\n{'='*50}")
        print("SUMMARY STATISTICS")
        print(f"{'='*50}")
        print(f"Total responses: {stats['total_responses']}")
        print(f"Average latency: {stats['avg_latency_seconds']}s")
        print(f"Total tokens: {stats['total_tokens']}")
        print(f"Cost: $0.00 (local inference)")
        print(f"Average response length: {stats['avg_response_length']} characters")
        
        print(f"\nResults saved to: {output_file}")
    else:
        print("No results to save.")

if __name__ == "__main__":
    main()