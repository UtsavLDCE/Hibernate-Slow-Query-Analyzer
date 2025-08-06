#!/usr/bin/env python3
"""
Slow Query Analyzer Script
==========================

This script analyzes slow query logs and provides top-k results based on various criteria.
It can analyze queries by frequency, execution time, and generate comprehensive reports.

Usage:
    python3 slow_query_analyzer.py <log_file> [options]

Example:
    python3 slow_query_analyzer.py repository.log --top-k 10 --sort-by hits
    python3 slow_query_analyzer.py repository.log --top-k 5 --sort-by time --format json
"""

import re
import sys
import json
import argparse
import tarfile
import gzip
import os
import tempfile
import glob
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Tuple
import csv

class SlowQueryAnalyzer:
    def __init__(self, log_input: str):
        self.log_input = log_input
        self.file_list = []
        self.queries = []
        self.query_groups = defaultdict(list)
        self.temp_files = []  # Track temporary files for cleanup
        self.file_stats = {}  # Track stats per file
        
    def _extract_from_tar_gz(self, tar_path: str) -> str:
        """Extract repository.log from tar.gz file and return content."""
        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                # Look for repository.log files in the archive
                log_files = [member for member in tar.getmembers() 
                            if member.isfile() and member.name.endswith('repository.log')]
                
                if not log_files:
                    print(f"No repository.log file found in {tar_path}")
                    return ""
                
                if len(log_files) > 1:
                    print(f"Multiple repository.log files found in {tar_path}:")
                    for i, log_file in enumerate(log_files, 1):
                        print(f"  {i}. {log_file.name}")
                    print(f"Using: {log_files[0].name}")
                
                # Extract the first (or only) repository.log file
                log_member = log_files[0]
                extracted_file = tar.extractfile(log_member)
                
                if extracted_file is None:
                    print(f"Could not extract {log_member.name} from {tar_path}")
                    return ""
                
                print(f"Extracted {log_member.name} from {tar_path} ({log_member.size} bytes)")
                return extracted_file.read().decode('utf-8', errors='ignore')
                
        except tarfile.TarError as e:
            print(f"Error reading tar.gz file {tar_path}: {e}")
            return ""
        except Exception as e:
            print(f"Error extracting from {tar_path}: {e}")
            return ""
    
    def _read_file_content(self, file_path: str) -> str:
        """Read content from regular file or compressed archive."""
        if file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            return self._extract_from_tar_gz(file_path)
        elif file_path.endswith('.gz'):
            # Handle standalone .gz files
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading gzip file {file_path}: {e}")
                return ""
        else:
            # Regular file
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return ""
    
    def _find_repository_files(self, input_path: str) -> List[str]:
        """Find all repository log files based on input pattern."""
        files = []
        
        if os.path.isfile(input_path):
            # Single file provided
            files = [input_path]
        elif os.path.isdir(input_path):
            # Directory provided - find all repository files
            patterns = [
                os.path.join(input_path, 'repository*.log'),
                os.path.join(input_path, 'repository*.gz'),
                os.path.join(input_path, 'repository*.tar.gz'),
                os.path.join(input_path, 'repository*.tgz')
            ]
            
            for pattern in patterns:
                files.extend(glob.glob(pattern))
        else:
            # Treat as glob pattern
            if '*' in input_path or '?' in input_path:
                files = glob.glob(input_path)
            else:
                # Try to find files with repository pattern in the same directory
                base_dir = os.path.dirname(input_path) or '.'
                patterns = [
                    os.path.join(base_dir, 'repository*.log'),
                    os.path.join(base_dir, 'repository*.gz'),
                    os.path.join(base_dir, 'repository*.tar.gz'),
                    os.path.join(base_dir, 'repository*.tgz')
                ]
                
                for pattern in patterns:
                    files.extend(glob.glob(pattern))
                    
                if not files:
                    files = [input_path]  # Fallback to original input
        
        # Remove duplicates and sort
        files = sorted(list(set(files)))
        
        # Filter out non-existent files
        existing_files = [f for f in files if os.path.exists(f)]
        
        return existing_files
    
    def _parse_single_file(self, file_path: str) -> int:
        """Parse a single file and return number of slow queries found."""
        print(f"Reading from: {file_path}")
        content = self._read_file_content(file_path)
        
        if not content:
            print(f"  No content could be read from {file_path}")
            return 0
        
        # Pattern to match slow query entries
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*?SlowQuery: (\d+) milliseconds\. SQL: \'.*?wrapping ([^\']*)\''
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            print(f"  No slow queries found in {file_path}")
            return 0
        
        file_queries = 0
        for timestamp, time_ms, query in matches:
            query_clean = query.strip()
            
            # Extract operation type and main table
            operation, table = self._extract_operation_and_table(query_clean)
            
            query_info = {
                'timestamp': timestamp,
                'execution_time': int(time_ms),
                'operation': operation,
                'table': table,
                'query_type': f'{operation} {table}',
                'query': query_clean,
                'query_preview': query_clean[:200] + '...' if len(query_clean) > 200 else query_clean,
                'source_file': os.path.basename(file_path)
            }
            
            self.queries.append(query_info)
            self.query_groups[query_info['query_type']].append(query_info)
            file_queries += 1
        
        print(f"  Found {file_queries} slow queries in {file_path}")
        
        # Store per-file stats
        self.file_stats[file_path] = {
            'queries': file_queries,
            'file_size': len(content),
            'basename': os.path.basename(file_path)
        }
        
        return file_queries
    
    def parse_log_files(self):
        """Parse log files and extract slow query information."""
        self.file_list = self._find_repository_files(self.log_input)
        
        if not self.file_list:
            print(f"Error: No files found matching '{self.log_input}'")
            return
        
        total_files = len(self.file_list)
        print(f"Found {total_files} file(s) to process:")
        for i, file_path in enumerate(self.file_list, 1):
            print(f"  {i}. {file_path}")
        print()
        
        total_queries = 0
        for file_path in self.file_list:
            queries_in_file = self._parse_single_file(file_path)
            total_queries += queries_in_file
        
        if total_queries == 0:
            print("No slow queries found in any files.")
            return
        
        print(f"\nSummary: Parsed {total_queries} slow queries from {len(self.file_list)} files, grouped into {len(self.query_groups)} query types.")
    
    def _extract_operation_and_table(self, query: str) -> Tuple[str, str]:
        """Extract operation type and main table from SQL query."""
        query_lower = query.lower()
        
        if query_lower.startswith('select'):
            from_match = re.search(r'from\s+(\w+)', query_lower)
            return 'SELECT', from_match.group(1) if from_match else 'unknown'
        elif query_lower.startswith('insert'):
            insert_match = re.search(r'insert\s+into\s+(\w+)', query_lower)
            return 'INSERT', insert_match.group(1) if insert_match else 'unknown'
        elif query_lower.startswith('update'):
            update_match = re.search(r'update\s+(\w+)', query_lower)
            return 'UPDATE', update_match.group(1) if update_match else 'unknown'
        elif query_lower.startswith('delete'):
            delete_match = re.search(r'delete\s+from\s+(\w+)', query_lower)
            return 'DELETE', delete_match.group(1) if delete_match else 'unknown'
        else:
            return 'OTHER', 'unknown'
    
    def get_top_k_by_hits(self, k: int = 10) -> List[Dict[str, Any]]:
        """Get top k query types by frequency (hits)."""
        results = []
        
        for query_type, query_list in self.query_groups.items():
            times = [q['execution_time'] for q in query_list]
            
            result = {
                'query_type': query_type,
                'hits': len(query_list),
                'total_time': sum(times),
                'avg_time': sum(times) / len(times),
                'max_time': max(times),
                'min_time': min(times),
                'sample_query': query_list[0]['query_preview'],
                'sample_timestamp': query_list[0]['timestamp']
            }
            results.append(result)
        
        # Sort by hits first, then by total time
        results.sort(key=lambda x: (x['hits'], x['total_time']), reverse=True)
        return results[:k]
    
    def get_top_k_by_time(self, k: int = 10) -> List[Dict[str, Any]]:
        """Get top k individual queries by execution time."""
        # Sort all queries by execution time
        sorted_queries = sorted(self.queries, key=lambda x: x['execution_time'], reverse=True)
        return sorted_queries[:k]
    
    def get_top_k_by_total_time(self, k: int = 10) -> List[Dict[str, Any]]:
        """Get top k query types by total execution time."""
        results = []
        
        for query_type, query_list in self.query_groups.items():
            times = [q['execution_time'] for q in query_list]
            
            result = {
                'query_type': query_type,
                'hits': len(query_list),
                'total_time': sum(times),
                'avg_time': sum(times) / len(times),
                'max_time': max(times),
                'min_time': min(times),
                'sample_query': query_list[0]['query_preview'],
                'sample_timestamp': query_list[0]['timestamp']
            }
            results.append(result)
        
        # Sort by total time
        results.sort(key=lambda x: x['total_time'], reverse=True)
        return results[:k]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        if not self.queries:
            return {}
        
        times = [q['execution_time'] for q in self.queries]
        
        # File-based statistics
        files_processed = len(self.file_list)
        source_files = {}
        for file_path, stats in self.file_stats.items():
            source_files[stats['basename']] = {
                'queries': stats['queries'],
                'file_size': stats['file_size']
            }
        
        return {
            'total_slow_queries': len(self.queries),
            'unique_query_types': len(self.query_groups),
            'files_processed': files_processed,
            'source_files': source_files,
            'total_execution_time': sum(times),
            'average_execution_time': sum(times) / len(times),
            'max_execution_time': max(times),
            'min_execution_time': min(times),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self, top_k: int = 10, sort_by: str = 'hits') -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        stats = self.get_statistics()
        
        report = {
            'statistics': stats,
            'top_by_hits': self.get_top_k_by_hits(top_k),
            'top_by_individual_time': self.get_top_k_by_time(top_k),
            'top_by_total_time': self.get_top_k_by_total_time(top_k)
        }
        
        return report
    
    def cleanup(self):
        """Clean up any temporary files created during processing."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Could not clean up temporary file {temp_file}: {e}")
        self.temp_files.clear()

def print_table_format(data: List[Dict], title: str, sort_by: str):
    """Print data in a formatted table."""
    print(f"\n{title}")
    print("=" * len(title))
    
    if sort_by == 'time' and 'execution_time' in data[0]:
        # Individual queries
        print(f"{'Rank':<5} {'Operation':<8} {'Table':<25} {'Time (ms)':<10} {'Timestamp':<20}")
        print("-" * 75)
        
        for i, item in enumerate(data, 1):
            print(f"{i:<5} {item['operation']:<8} {item['table']:<25} {item['execution_time']:<10} {item['timestamp']:<20}")
    else:
        # Query groups
        print(f"{'Rank':<5} {'Query Type':<35} {'Hits':<6} {'Total(ms)':<10} {'Avg(ms)':<8} {'Max(ms)':<8}")
        print("-" * 75)
        
        for i, item in enumerate(data, 1):
            print(f"{i:<5} {item['query_type']:<35} {item['hits']:<6} {item['total_time']:<10} {item['avg_time']:<8.0f} {item['max_time']:<8}")

def print_detailed_format(data: List[Dict], title: str, sort_by: str):
    """Print data in detailed format."""
    print(f"\n{title}")
    print("=" * len(title))
    
    if sort_by == 'time' and 'execution_time' in data[0]:
        # Individual queries
        for i, item in enumerate(data, 1):
            print(f"\n{i}. {item['operation']} {item['table']} - {item['execution_time']}ms")
            print(f"   Timestamp: {item['timestamp']}")
            print(f"   Query: {item['query_preview']}")
    else:
        # Query groups
        for i, item in enumerate(data, 1):
            print(f"\n{i}. {item['query_type']}")
            print(f"   Hits: {item['hits']}, Total: {item['total_time']}ms, Avg: {item['avg_time']:.0f}ms")
            print(f"   Range: {item['min_time']}ms - {item['max_time']}ms")
            print(f"   Sample: {item['sample_query']}")

def export_to_csv(data: List[Dict], filename: str, sort_by: str):
    """Export data to CSV format."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        if sort_by == 'time' and 'execution_time' in data[0]:
            fieldnames = ['rank', 'operation', 'table', 'execution_time', 'timestamp', 'query_preview']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, item in enumerate(data, 1):
                writer.writerow({
                    'rank': i,
                    'operation': item['operation'],
                    'table': item['table'],
                    'execution_time': item['execution_time'],
                    'timestamp': item['timestamp'],
                    'query_preview': item['query_preview']
                })
        else:
            fieldnames = ['rank', 'query_type', 'hits', 'total_time', 'avg_time', 'max_time', 'min_time', 'sample_query']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, item in enumerate(data, 1):
                writer.writerow({
                    'rank': i,
                    'query_type': item['query_type'],
                    'hits': item['hits'],
                    'total_time': item['total_time'],
                    'avg_time': round(item['avg_time']),
                    'max_time': item['max_time'],
                    'min_time': item['min_time'],
                    'sample_query': item['sample_query']
                })
    
    print(f"Data exported to {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Analyze slow queries from log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s repository.log --top-k 10 --sort-by hits
  %(prog)s repository.log --top-k 5 --sort-by time --format json
  %(prog)s repository.log --sort-by total-time --export-csv results.csv
  %(prog)s repository.log --detailed --top-k 3
        """
    )
    
    parser.add_argument('log_input', help='Path to log file, directory, or pattern (e.g., repository.log, /logs/, "repository*")')
    parser.add_argument('--top-k', '-k', type=int, default=10, 
                       help='Number of top results to show (default: 10)')
    parser.add_argument('--sort-by', choices=['hits', 'time', 'total-time'], default='hits',
                       help='Sort results by: hits (frequency), time (individual), or total-time (default: hits)')
    parser.add_argument('--format', choices=['table', 'detailed', 'json'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--export-csv', metavar='FILENAME',
                       help='Export results to CSV file')
    parser.add_argument('--export-json', metavar='FILENAME',
                       help='Export full report to JSON file')
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed output (equivalent to --format detailed)')
    parser.add_argument('--stats-only', action='store_true',
                       help='Show only statistics')
    parser.add_argument('--list-files', action='store_true',
                       help='List files that would be processed and exit')
    
    args = parser.parse_args()
    
    if args.detailed:
        args.format = 'detailed'
    
    # Initialize analyzer
    analyzer = SlowQueryAnalyzer(args.log_input)
    
    # Handle list-files option
    if args.list_files:
        files = analyzer._find_repository_files(args.log_input)
        if files:
            print(f"Found {len(files)} file(s) matching '{args.log_input}':")
            for i, file_path in enumerate(files, 1):
                size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                print(f"  {i}. {file_path} ({size:,} bytes)")
        else:
            print(f"No files found matching '{args.log_input}'")
        return
    
    try:
        analyzer.parse_log_files()
        
        if not analyzer.queries:
            return
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        analyzer.cleanup()
        return
    except Exception as e:
        print(f"Error during analysis: {e}")
        analyzer.cleanup()
        return
    
    # Get statistics
    stats = analyzer.get_statistics()
    
    if args.stats_only:
        print("\nSTATISTICS")
        print("=" * 20)
        for key, value in stats.items():
            if key == 'source_files':
                print(f"Source Files:")
                for filename, file_stats in value.items():
                    print(f"  {filename}: {file_stats['queries']} queries ({file_stats['file_size']:,} bytes)")
            elif key != 'analysis_timestamp':
                print(f"{key.replace('_', ' ').title()}: {value}")
        return
    
    # Get data based on sort criteria
    if args.sort_by == 'hits':
        data = analyzer.get_top_k_by_hits(args.top_k)
        title = f"TOP {args.top_k} QUERIES BY FREQUENCY (MOST HITS)"
    elif args.sort_by == 'time':
        data = analyzer.get_top_k_by_time(args.top_k)
        title = f"TOP {args.top_k} SLOWEST INDIVIDUAL QUERIES"
    else:  # total-time
        data = analyzer.get_top_k_by_total_time(args.top_k)
        title = f"TOP {args.top_k} QUERIES BY TOTAL EXECUTION TIME"
    
    # Display results
    if args.format == 'json':
        result = {
            'statistics': stats,
            'data': data,
            'sort_by': args.sort_by,
            'top_k': args.top_k
        }
        print(json.dumps(result, indent=2))
    elif args.format == 'detailed':
        # Show stats first
        print("\nSTATISTICS")
        print("=" * 20)
        for key, value in stats.items():
            if key != 'analysis_timestamp':
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print_detailed_format(data, title, args.sort_by)
    else:
        # Show stats first
        print("\nSTATISTICS")
        print("=" * 20)
        for key, value in stats.items():
            if key != 'analysis_timestamp':
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print_table_format(data, title, args.sort_by)
    
    # Export options
    if args.export_csv:
        export_to_csv(data, args.export_csv, args.sort_by)
    
    if args.export_json:
        full_report = analyzer.generate_report(args.top_k, args.sort_by)
        with open(args.export_json, 'w') as f:
            json.dump(full_report, f, indent=2)
        print(f"Full report exported to {args.export_json}")
    
    # Cleanup
    analyzer.cleanup()

if __name__ == "__main__":
    main()
