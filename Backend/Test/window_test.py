import os
import sys
import argparse
import time
from tabulate import tabulate
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

# Fix the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Backend.celery_client import CeleryClient
from Test_Utils import process_file

def run_window_size_tests(file_path, client, start_size, num_tests, increment, output_dir, debug=False):
    """
    Run compression tests with different window sizes on the same file.
    
    Args:
        file_path: Path to the test file
        client: The CeleryClient instance
        start_size: Starting window size
        num_tests: Number of tests to run
        increment: Window size increment between tests
        output_dir: Base output directory
        debug: Whether to save debug information
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    for i in range(num_tests):
        window_size = start_size + (i * increment)
        
        # Create test-specific output directory
        test_output = os.path.join(output_dir, f"window_size_{window_size}")
        os.makedirs(test_output, exist_ok=True)
        
        print(f"\n=== Test {i+1}/{num_tests}: Window Size = {window_size} ===")
        result = process_file(file_path, client, window_size, test_output, verbose=True, debug=debug)
        
        # Add window size to result
        result["window_size"] = window_size
        results.append(result)
        
    return results

def display_table_results(results):
    """
    Display test results in a table format.
    
    Args:
        results: List of test result dictionaries
    """
    table_data = []
    for r in results:
        row = [
            r["window_size"],
            f"{r['original_size']:,} bytes",
            f"{r['compressed_size']:,} bytes",
            f"{r['compression_ratio']:.2f}x",
            f"{(1 - r['compressed_size']/r['original_size']) * 100:.2f}%",
            f"{r['compression_time']:.2f}s",
            f"{r['decompression_time']:.2f}s",
            "Yes" if r["identical"] else "No"
        ]
        table_data.append(row)
    
    headers = ["Window Size", "Original Size", "Compressed Size", "Ratio", 
               "Space Savings", "Comp Time", "Decomp Time", "Files Match"]
    
    print("\n=== Window Size Benchmark Results ===")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def export_csv(results, output_dir, file_name):
    """
    Export results to CSV for external analysis.
    
    Args:
        results: List of test result dictionaries
        output_dir: Directory to save CSV
        file_name: Name of the tested file
    """
    import csv
    
    csv_path = os.path.join(output_dir, f"{file_name}_benchmark_results.csv")
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            "Window Size", "Original Size", "Compressed Size", 
            "Compression Ratio", "Space Savings", 
            "Compression Time", "Decompression Time",
            "Files Identical"
        ])
        
        # Write data rows
        for r in results:
            writer.writerow([
                r["window_size"],
                r["original_size"],
                r["compressed_size"],
                r["compression_ratio"],
                (1 - r["compressed_size"]/r["original_size"]) * 100,
                r["compression_time"],
                r["decompression_time"],
                r["identical"]
            ])
    
    print(f"\nResults exported to CSV: {csv_path}")
    return csv_path

def plot_results(results, output_dir, file_name):
    """
    Create plots of the test results.
    
    Args:
        results: List of test result dictionaries
        output_dir: Directory to save plots
        file_name: Name of the tested file
    """
    try:
        window_sizes = [r["window_size"] for r in results]
        compression_ratios = [r["compression_ratio"] for r in results]
        compression_times = [r["compression_time"] for r in results]
        decompression_times = [r["decompression_time"] for r in results]
        
        # Create figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Plot compression ratio
        ax1.plot(window_sizes, compression_ratios, 'bo-', linewidth=2)
        ax1.set_title(f'Compression Ratio vs Window Size for {file_name}')
        ax1.set_xlabel('Window Size')
        ax1.set_ylabel('Compression Ratio (higher is better)')
        ax1.grid(True)
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Annotate points with values
        for i, ratio in enumerate(compression_ratios):
            ax1.annotate(f"{ratio:.2f}x", 
                        (window_sizes[i], ratio),
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center')
        
        # Plot processing times
        ax2.plot(window_sizes, compression_times, 'ro-', label='Compression Time', linewidth=2)
        ax2.plot(window_sizes, decompression_times, 'go-', label='Decompression Time', linewidth=2)
        ax2.set_title(f'Processing Time vs Window Size for {file_name}')
        ax2.set_xlabel('Window Size')
        ax2.set_ylabel('Time (seconds)')
        ax2.grid(True)
        ax2.legend()
        ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Adjust layout and save
        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"{file_name}_window_size_benchmark.png")
        plt.savefig(plot_path)
        print(f"\nPlot saved to: {plot_path}")
        
        # Create a second plot for the compression ratio vs processing time tradeoff
        fig2, ax3 = plt.subplots(figsize=(10, 6))
        total_times = [c + d for c, d in zip(compression_times, decompression_times)]
        
        # Create scatter plot with point size based on window size
        sizes = [ws * 3 for ws in window_sizes]  # Scale for visibility
        scatter = ax3.scatter(total_times, compression_ratios, s=sizes, 
                             c=window_sizes, cmap='viridis', alpha=0.7)
        
        # Add colorbar for window size
        cbar = plt.colorbar(scatter)
        cbar.set_label('Window Size')
        
        # Connect points in order of window size
        ax3.plot(total_times, compression_ratios, 'k--', alpha=0.5)
        
        # Annotate points with window size values
        for i, ws in enumerate(window_sizes):
            ax3.annotate(f"w={ws}", 
                        (total_times[i], compression_ratios[i]),
                        textcoords="offset points", 
                        xytext=(5,5))
        
        ax3.set_title(f'Compression Ratio vs Total Processing Time for {file_name}')
        ax3.set_xlabel('Total Processing Time (seconds)')
        ax3.set_ylabel('Compression Ratio (higher is better)')
        ax3.grid(True)
        
        # Save the second plot
        tradeoff_path = os.path.join(output_dir, f"{file_name}_ratio_time_tradeoff.png")
        plt.savefig(tradeoff_path)
        print(f"Tradeoff plot saved to: {tradeoff_path}")
        
    except Exception as e:
        print(f"\nError creating plots: {e}")
        print("Matplotlib may not be installed. Install with: pip install matplotlib")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLMPress compression with different window sizes")
    parser.add_argument("--input", "-i", required=True, help="Path to the file to compress")
    parser.add_argument("--output", "-o", default="Output/WindowTest", help="Output directory for results")
    parser.add_argument("--start-size", "-s", type=int, default=16, help="Starting window size (default: 16)")
    parser.add_argument("--num-tests", "-n", type=int, default=8, help="Number of tests to run (default: 8)")
    parser.add_argument("--increment", "-inc", type=int, default=16, help="Window size increment (default: 16)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save token information")
    parser.add_argument("--plot", "-p", action="store_true", help="Generate plots of results (requires matplotlib)")
    parser.add_argument("--csv", "-c", action="store_true", help="Export results to CSV file")
    
    args = parser.parse_args()
    
    # Validate file path
    if not os.path.isfile(args.input):
        print(f"Error: File '{args.input}' does not exist or is not a file")
        return
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Get file name for display
    file_name = os.path.basename(args.input)
    
    # Create API client
    api = CeleryClient()
    
    # Print test configuration
    print("\n=== Window Size Benchmark Configuration ===")
    print(f"Input file: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"Window size range: {args.start_size} to {args.start_size + (args.num_tests-1) * args.increment}")
    print(f"Number of tests: {args.num_tests}")
    print(f"Window size increment: {args.increment}")
    
    # Run the benchmark
    start_time = time.time()
    results = run_window_size_tests(
        args.input, 
        api, 
        args.start_size, 
        args.num_tests, 
        args.increment, 
        args.output, 
        args.debug
    )
    total_time = time.time() - start_time
    
    # Display results table
    display_table_results(results)
    
    # Export to CSV if requested
    if args.csv:
        export_csv(results, args.output, file_name)
    
    # Create plots if requested
    if args.plot:
        plot_results(results, args.output, file_name)
    
    # Print summary
    print(f"\nBenchmark completed in {total_time:.2f} seconds")
    
    # Find optimal window size based on compression ratio
    best_ratio_result = max(results, key=lambda r: r["compression_ratio"])
    best_ratio_window = best_ratio_result["window_size"]
    
    # Find optimal window size based on total processing time
    best_time_result = min(results, key=lambda r: r["compression_time"] + r["decompression_time"])
    best_time_window = best_time_result["window_size"]
    
    print("\n=== Recommendations ===")
    print(f"Best compression ratio: Window size = {best_ratio_window} ({best_ratio_result['compression_ratio']:.2f}x)")
    print(f"Fastest processing time: Window size = {best_time_window} ({best_time_result['compression_time'] + best_time_result['decompression_time']:.2f}s)")


if __name__ == "__main__":
    main()