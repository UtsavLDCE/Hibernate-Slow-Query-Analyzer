# Slow Query Analyzer - Usage Guide

## Overview

The `slow_query_analyzer.py` script is a powerful tool for analyzing slow query logs and identifying performance bottlenecks in your database operations. It can parse log files, extract slow queries, and provide various analyses including frequency, execution time, and comprehensive statistics.

## Features

- **Multiple Analysis Types**: Sort by frequency (hits), individual execution time, or total execution time
- **Flexible Output Formats**: Table, detailed text, or JSON output
- **Export Options**: CSV and JSON export capabilities  
- **Configurable Results**: Specify top-k results (default: 10)
- **Comprehensive Statistics**: Overall performance metrics
- **Query Categorization**: Automatically categorizes queries by operation and table
- **Compressed File Support**: Works with .tar.gz, .tgz, and .gz files
- **Archive Intelligence**: Automatically finds repository.log files in archives

## Basic Usage

```bash
python3 slow_query_analyzer.py <log_file> [options]
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--top-k, -k` | Number of top results to show | 10 |
| `--sort-by` | Sort criteria: `hits`, `time`, `total-time` | `hits` |
| `--format` | Output format: `table`, `detailed`, `json` | `table` |
| `--detailed` | Show detailed output (same as `--format detailed`) | - |
| `--stats-only` | Show only statistics without query details | - |
| `--export-csv` | Export results to CSV file | - |
| `--export-json` | Export full report to JSON file | - |

## Usage Examples

### 1. Basic Analysis (Top 10 queries by frequency)
```bash
python3 slow_query_analyzer.py repository.log
```

### 2. Analysis from compressed archive
```bash
python3 slow_query_analyzer.py logs_20250806.tar.gz --top-k 10
```

### 3. Top 5 slowest individual queries from gzipped file
```bash
python3 slow_query_analyzer.py repository.log.gz --top-k 5 --sort-by time
```

### 4. Detailed analysis of top 3 queries by total execution time
```bash
python3 slow_query_analyzer.py repository.log --top-k 3 --sort-by total-time --detailed
```

### 5. JSON output for integration with other tools
```bash
python3 slow_query_analyzer.py logs_archive.tar.gz --top-k 10 --format json
```

### 6. Export results to CSV from compressed archive
```bash
python3 slow_query_analyzer.py logs_backup.tar.gz --sort-by hits --export-csv results.csv
```

### 7. Generate comprehensive JSON report
```bash
python3 slow_query_analyzer.py repository.log.gz --export-json full_report.json
```

### 8. Show only statistics
```bash
python3 slow_query_analyzer.py repository.log --stats-only
```

## Sort Options Explained

### `--sort-by hits` (Default)
- Shows query types with the **most frequent occurrences**
- Best for identifying queries that are repeatedly slow
- Useful for finding queries that need optimization due to high frequency

### `--sort-by time` 
- Shows **individual queries** with the longest execution times
- Best for identifying the absolute worst performing queries
- Useful for finding specific query instances that are extremely slow

### `--sort-by total-time`
- Shows query types with the **highest cumulative execution time**
- Best for identifying queries that consume the most total database time
- Useful for understanding overall impact on system performance

## Output Formats

### Table Format (Default)
Clean, tabular display suitable for terminal viewing:
```
STATISTICS
====================
Total Slow Queries: 52
Unique Query Types: 20
...

TOP 5 QUERIES BY FREQUENCY (MOST HITS)
======================================
Rank  Query Type                          Hits   Total(ms)  Avg(ms)  Max(ms) 
---------------------------------------------------------------------------
1     SELECT softwarecomponent            9      4720       524      1158    
```

### Detailed Format
Comprehensive output with query previews:
```
1. SELECT softwarecomponent
   Hits: 9, Total: 4720ms, Avg: 524ms
   Range: 141ms - 1158ms
   Sample: select softwareco0_.id as id1_862_...
```

### JSON Format
Structured output for programmatic processing:
```json
{
  "statistics": {
    "total_slow_queries": 52,
    "unique_query_types": 20,
    ...
  },
  "data": [
    {
      "query_type": "SELECT softwarecomponent",
      "hits": 9,
      "total_time": 4720,
      ...
    }
  ]
}
```

## Real-World Examples

### Performance Troubleshooting
```bash
# Find the most problematic queries
python3 slow_query_analyzer.py app.log --sort-by total-time --detailed

# Identify frequent slow queries that need optimization
python3 slow_query_analyzer.py app.log --sort-by hits --top-k 20

# Find the absolute slowest queries
python3 slow_query_analyzer.py app.log --sort-by time --top-k 5 --detailed
```

### Reporting and Documentation
```bash
# Generate comprehensive report for management
python3 slow_query_analyzer.py app.log --export-json weekly_report.json

# Create CSV for spreadsheet analysis
python3 slow_query_analyzer.py app.log --sort-by total-time --export-csv performance_data.csv

# Quick stats overview
python3 slow_query_analyzer.py app.log --stats-only
```

### Integration with Other Tools
```bash
# Pipeline with other analysis tools
python3 slow_query_analyzer.py app.log --format json | jq '.statistics.total_slow_queries'

# Automated monitoring
python3 slow_query_analyzer.py app.log --stats-only | grep "Max Execution Time"
```

## Understanding the Output

### Statistics Section
- **Total Slow Queries**: Number of slow query entries found
- **Unique Query Types**: Number of different query patterns
- **Total Execution Time**: Sum of all slow query execution times
- **Average Execution Time**: Mean execution time across all slow queries
- **Max/Min Execution Time**: Range of execution times

### Query Metrics
- **Hits**: Number of times this query type appeared as slow
- **Total(ms)**: Sum of execution times for this query type
- **Avg(ms)**: Average execution time for this query type
- **Max(ms)**: Longest execution time for this query type
- **Min(ms)**: Shortest execution time for this query type

## Tips for Effective Analysis

1. **Start with frequency analysis** (`--sort-by hits`) to identify the most common problems
2. **Use detailed format** for understanding specific query patterns
3. **Export to JSON** for further analysis or integration with monitoring tools
4. **Compare different time periods** by analyzing multiple log files
5. **Focus on high-impact queries** that combine both high frequency and high execution time

## Troubleshooting

### No slow queries found
- Check that your log file contains the expected format
- Verify the slow query pattern matches your log format
- The script looks for: `SlowQuery: X milliseconds. SQL: 'HikariProxy...`

### Memory issues with large files
- The script loads the entire file into memory
- For very large files (>1GB), consider splitting the log file first

### Character encoding issues
- The script uses UTF-8 with error ignoring
- Most log files should work without issues

## Supported File Types

The script supports multiple input formats:

### Regular Files
- `repository.log`
- `application.log` 
- Any text file with slow query entries

### Compressed Files
- **Gzip compressed**: `repository.log.gz`, `app.log.gz`
- **Tar.gz archives**: `logs_20250806.tar.gz`, `backup.tgz`
- **Mixed archives**: Archives containing multiple files

### Archive Processing Features
- Automatically detects and extracts `repository.log` files from archives
- Handles nested directory structures (e.g., `logs/nested/repository.log`)
- Memory-efficient processing (no temporary files created)
- Supports multiple repository.log files in one archive (uses first found)

## Log Format Requirements

The script expects log entries in this format:
```
YYYY-MM-DD HH:mm:ss.sss ... SlowQuery: XXX milliseconds. SQL: 'HikariProxyPreparedStatement@... wrapping ACTUAL_SQL_QUERY'
```

This format is common in many Java-based applications using HikariCP connection pooling.

## Sample Output from Your Repository.log

Using your actual data:
```bash
$ python3 slow_query_analyzer.py repository.log --top-k 5

STATISTICS
====================
Total Slow Queries: 52
Unique Query Types: 20
Total Execution Time: 32312ms
Average Execution Time: 621ms
Max Execution Time: 2648ms

TOP 5 QUERIES BY FREQUENCY (MOST HITS)
======================================
Rank  Query Type                          Hits   Total(ms)  Avg(ms)  Max(ms) 
---------------------------------------------------------------------------
1     SELECT softwarecomponent            9      4720       524      1158    
2     INSERT assetchangelogcomponentdata  6      5927       988      1025    
3     INSERT assetchangelog               5      5907       1181     2648    
4     SELECT ssoconfig                    5      3560       712      1062    
5     SELECT flotouser                    4      1910       478      589     
```
