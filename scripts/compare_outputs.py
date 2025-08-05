#!/usr/bin/env python3
"""
Compare outputs between OpenAI GPT-4 and local GPT-OSS-20B model.
Generates side-by-side comparisons and performance analysis.
"""

import json
import argparse
import pandas as pd
from typing import List, Dict, Any
from utils import load_prompts, create_comparison_summary

def load_results(file_path: str) -> List[Dict[str, Any]]:
    """Load results from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Results file not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return []

def create_side_by_side_comparison(openai_results: List[Dict], local_results: List[Dict]) -> List[Dict[str, Any]]:
    """Create side-by-side comparison of responses for the same prompts."""
    
    # Create lookup dictionaries
    openai_lookup = {result['prompt_id']: result for result in openai_results}
    local_lookup = {result['prompt_id']: result for result in local_results}
    
    # Find common prompt IDs
    common_prompts = set(openai_lookup.keys()) & set(local_lookup.keys())
    
    if not common_prompts:
        print("Warning: No common prompts found between OpenAI and local results")
        return []
    
    comparisons = []
    
    for prompt_id in sorted(common_prompts):
        openai_result = openai_lookup[prompt_id]
        local_result = local_lookup[prompt_id]
        
        comparison = {
            "prompt_id": prompt_id,
            "category": openai_result.get('category', 'unknown'),
            "openai": {
                "model": openai_result['model'],
                "response": openai_result['response'],
                "latency_seconds": openai_result['latency_seconds'],
                "total_tokens": openai_result.get('total_tokens', 0),
                "cost_usd": openai_result.get('cost_usd', 0),
                "response_length": openai_result['response_length'],
                "words_count": openai_result.get('words_count', 0),
                "has_error": openai_result.get('error', False)
            },
            "local": {
                "model": local_result['model'],
                "response": local_result['response'],
                "latency_seconds": local_result['latency_seconds'],
                "total_tokens": local_result.get('total_tokens', 0),
                "cost_usd": 0.0,  # Local inference is free
                "response_length": local_result['response_length'],
                "words_count": local_result.get('words_count', 0),
                "has_error": local_result.get('error', False)
            },
            "comparison_metrics": {
                "latency_ratio": local_result['latency_seconds'] / max(openai_result['latency_seconds'], 0.001),
                "length_ratio": local_result['response_length'] / max(openai_result['response_length'], 1),
                "cost_savings": openai_result.get('cost_usd', 0),
                "both_successful": not (openai_result.get('error', False) or local_result.get('error', False))
            }
        }
        
        comparisons.append(comparison)
    
    return comparisons

def generate_performance_analysis(comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate detailed performance analysis from comparisons."""
    
    if not comparisons:
        return {"error": "No comparisons available"}
    
    # Filter successful comparisons
    successful_comparisons = [c for c in comparisons if c['comparison_metrics']['both_successful']]
    
    if not successful_comparisons:
        return {"error": "No successful comparisons available"}
    
    # Calculate aggregate metrics
    total_comparisons = len(comparisons)
    successful_rate = len(successful_comparisons) / total_comparisons
    
    # Latency analysis
    latency_ratios = [c['comparison_metrics']['latency_ratio'] for c in successful_comparisons]
    avg_latency_ratio = sum(latency_ratios) / len(latency_ratios)
    
    # Response length analysis
    length_ratios = [c['comparison_metrics']['length_ratio'] for c in successful_comparisons]
    avg_length_ratio = sum(length_ratios) / len(length_ratios)
    
    # Cost analysis
    total_openai_cost = sum(c['openai']['cost_usd'] for c in successful_comparisons)
    
    # Category breakdown
    category_analysis = {}
    for comparison in successful_comparisons:
        category = comparison['category']
        if category not in category_analysis:
            category_analysis[category] = {
                'count': 0,
                'avg_latency_ratio': 0,
                'avg_length_ratio': 0,
                'total_cost_savings': 0
            }
        
        category_analysis[category]['count'] += 1
        category_analysis[category]['avg_latency_ratio'] += comparison['comparison_metrics']['latency_ratio']
        category_analysis[category]['avg_length_ratio'] += comparison['comparison_metrics']['length_ratio']
        category_analysis[category]['total_cost_savings'] += comparison['comparison_metrics']['cost_savings']
    
    # Calculate averages for categories
    for category in category_analysis:
        count = category_analysis[category]['count']
        category_analysis[category]['avg_latency_ratio'] /= count
        category_analysis[category]['avg_length_ratio'] /= count
    
    return {
        "overview": {
            "total_comparisons": total_comparisons,
            "successful_comparisons": len(successful_comparisons),
            "success_rate": round(successful_rate * 100, 1),
            "avg_latency_ratio": round(avg_latency_ratio, 2),
            "avg_response_length_ratio": round(avg_length_ratio, 2),
            "total_cost_savings": round(total_openai_cost, 4)
        },
        "performance_summary": {
            "local_vs_openai_speed": f"{'Faster' if avg_latency_ratio < 1 else 'Slower'} by {abs(1-avg_latency_ratio):.1f}x",
            "local_vs_openai_length": f"{'Shorter' if avg_length_ratio < 1 else 'Longer'} by {abs(1-avg_length_ratio):.1f}x",
            "cost_efficiency": f"${total_openai_cost:.4f} saved with local inference"
        },
        "category_breakdown": category_analysis
    }

def generate_csv_export(comparisons: List[Dict[str, Any]], output_file: str):
    """Export comparison data to CSV for further analysis."""
    
    if not comparisons:
        print("No comparisons to export")
        return
    
    # Flatten comparison data for CSV
    csv_data = []
    
    for comp in comparisons:
        row = {
            'prompt_id': comp['prompt_id'],
            'category': comp['category'],
            'openai_model': comp['openai']['model'],
            'local_model': comp['local']['model'],
            'openai_latency': comp['openai']['latency_seconds'],
            'local_latency': comp['local']['latency_seconds'],
            'openai_tokens': comp['openai']['total_tokens'],
            'local_tokens': comp['local']['total_tokens'],
            'openai_cost': comp['openai']['cost_usd'],
            'openai_response_length': comp['openai']['response_length'],
            'local_response_length': comp['local']['response_length'],
            'openai_words': comp['openai']['words_count'],
            'local_words': comp['local']['words_count'],
            'latency_ratio': comp['comparison_metrics']['latency_ratio'],
            'length_ratio': comp['comparison_metrics']['length_ratio'],
            'cost_savings': comp['comparison_metrics']['cost_savings'],
            'both_successful': comp['comparison_metrics']['both_successful'],
            'openai_has_error': comp['openai']['has_error'],
            'local_has_error': comp['local']['has_error']
        }
        csv_data.append(row)
    
    # Convert to DataFrame and save
    df = pd.DataFrame(csv_data)
    df.to_csv(output_file, index=False)
    print(f"CSV export saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Compare OpenAI and local model outputs")
    parser.add_argument("--openai-results", default="../results/openai_outputs.json", 
                       help="OpenAI results JSON file")
    parser.add_argument("--local-results", default="../results/local_outputs.json", 
                       help="Local model results JSON file")
    parser.add_argument("--output-dir", default="../results", help="Output directory")
    parser.add_argument("--export-csv", action="store_true", help="Export results to CSV")
    
    args = parser.parse_args()
    
    print("Loading results...")
    
    # Load results
    openai_results = load_results(args.openai_results)
    local_results = load_results(args.local_results)
    
    if not openai_results and not local_results:
        print("Error: No results found to compare")
        return
    
    if not openai_results:
        print("Warning: No OpenAI results found")
    
    if not local_results:
        print("Warning: No local results found")
    
    print(f"Loaded {len(openai_results)} OpenAI results and {len(local_results)} local results")
    
    # Create comparisons
    print("Creating side-by-side comparisons...")
    comparisons = create_side_by_side_comparison(openai_results, local_results)
    
    if not comparisons:
        print("No comparisons could be created")
        return
    
    print(f"Created {len(comparisons)} comparisons")
    
    # Generate analysis
    print("Generating performance analysis...")
    analysis = generate_performance_analysis(comparisons)
    
    # Save detailed comparison
    comparison_file = f"{args.output_dir}/detailed_comparison.json"
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparisons, f, indent=2, ensure_ascii=False)
    
    # Save analysis
    analysis_file = f"{args.output_dir}/performance_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    # Export CSV if requested
    if args.export_csv:
        csv_file = f"{args.output_dir}/comparison_data.csv"
        generate_csv_export(comparisons, csv_file)
    
    # Display summary
    print(f"\n{'='*60}")
    print("COMPARISON ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    if 'error' not in analysis:
        overview = analysis['overview']
        summary = analysis['performance_summary']
        
        print(f"Total comparisons: {overview['total_comparisons']}")
        print(f"Successful comparisons: {overview['successful_comparisons']} ({overview['success_rate']}%)")
        print(f"Average latency ratio (local/OpenAI): {overview['avg_latency_ratio']}")
        print(f"Average response length ratio: {overview['avg_response_length_ratio']}")
        print(f"Total cost savings: ${overview['total_cost_savings']}")
        print(f"\nPerformance Summary:")
        print(f"  Speed: Local model is {summary['local_vs_openai_speed']}")
        print(f"  Response length: Local responses are {summary['local_vs_openai_length']}")
        print(f"  Cost efficiency: {summary['cost_efficiency']}")
        
        print(f"\nCategory Breakdown:")
        for category, data in analysis['category_breakdown'].items():
            print(f"  {category.upper()}: {data['count']} comparisons, "
                  f"{data['avg_latency_ratio']:.2f}x latency ratio, "
                  f"${data['total_cost_savings']:.4f} saved")
    else:
        print(f"Analysis error: {analysis['error']}")
    
    print(f"\nResults saved to:")
    print(f"  Detailed comparison: {comparison_file}")
    print(f"  Performance analysis: {analysis_file}")
    if args.export_csv:
        print(f"  CSV export: {csv_file}")

if __name__ == "__main__":
    main()