# Multi-File Slow Query Analyzer - New Features

## 🌟 Major Enhancement: Multi-File Processing

Your slow query analyzer now supports **analyzing ALL repository files in a single run**, giving you comprehensive insights across multiple log files, different time periods, and various file formats.

## 🚀 What's New

### 1. **Directory Processing**
```bash
# Analyze ALL repository files in current directory
./analyze_queries.sh .

# Analyze ALL repository files in specific directory  
./analyze_queries.sh /path/to/logs/

# Advanced: Process with custom settings
python3 slow_query_analyzer.py /logs/ --top-k 20 --sort-by total-time
```

### 2. **Pattern Matching**
```bash
# Process only compressed repository files
./analyze_queries.sh 'repository*.gz'

# Process files from specific date range
python3 slow_query_analyzer.py 'repository_2025*.log' --detailed

# Process specific backup files
python3 slow_query_analyzer.py 'repository_backup*' --export-csv backup_analysis.csv
```

### 3. **File Discovery**
```bash
# List all files that would be processed (before running analysis)
./analyze_queries.sh . list
python3 slow_query_analyzer.py /logs/ --list-files

# See exactly what files match your pattern
python3 slow_query_analyzer.py 'repository*' --list-files
```

## 📊 Enhanced Statistics

When processing multiple files, you now get:

### Per-File Breakdown
```
Source Files:
  repository.log: 52 queries (101,745 bytes)
  repository_backup.log: 48 queries (95,432 bytes)  
  repository_old.gz: 35 queries (78,123 bytes)
```

### Aggregate Analysis
- **Combined query counts** across all files
- **Total execution times** summed up
- **Pattern detection** across time periods
- **File comparison** capabilities

## 🎯 Real-World Use Cases

### 1. **Comprehensive Log Analysis**
```bash
# Analyze entire log directory for the week
./analyze_queries.sh /var/logs/repository/ all

# Find patterns across multiple backup files
./analyze_queries.sh 'repository_backup_*' impact
```

### 2. **Historical Analysis**
```bash
# Compare performance across different time periods
python3 slow_query_analyzer.py 'repository_202501*' --export-json january.json
python3 slow_query_analyzer.py 'repository_202502*' --export-json february.json

# Analyze archived logs
./analyze_queries.sh 'logs_archive_*.tar.gz' detailed
```

### 3. **Development & Testing**
```bash
# Analyze all test environment logs
./analyze_queries.sh /test-logs/ frequent

# Compare production vs staging performance
./analyze_queries.sh /prod-logs/ --export-csv prod.csv
./analyze_queries.sh /staging-logs/ --export-csv staging.csv
```

## 🔍 Smart File Discovery

The enhanced script automatically finds files using these patterns:

### Automatic Patterns
- `repository*.log` - All repository log files
- `repository*.gz` - All compressed repository files  
- `repository*.tar.gz` - All repository archives
- `repository*.tgz` - Alternative archive format

### Directory Structure Support
```
logs/
├── repository.log
├── repository_backup.log
├── repository_old.gz
├── archived/
│   ├── repository_jan.tar.gz
│   └── repository_feb.tar.gz
└── temp/
    └── repository_debug.log
```

All these files can be processed in one command: `./analyze_queries.sh logs/`

## 💡 Key Benefits

### 1. **Time Savings**
- No need to analyze files one by one
- Single command processes entire directories
- Automated file discovery

### 2. **Comprehensive Insights**
- See patterns across multiple time periods
- Identify trending performance issues
- Compare query behavior over time

### 3. **Flexibility**
- Mix different file formats (regular, compressed, archived)
- Use patterns to select specific subsets
- Process historical data efficiently

### 4. **Scalability**
- Handle dozens of log files efficiently
- Memory-optimized processing
- Progress tracking for large datasets

## 📈 Example: Multi-File Analysis Results

When analyzing 5 repository files:

```
Found 5 file(s) to process:
  1. repository.log
  2. repository_backup.log  
  3. repository_old.gz
  4. repository_archive.tar.gz
  5. repository_debug.log

Summary: Parsed 267 slow queries from 5 files, grouped into 23 query types.

STATISTICS
==========
Total Slow Queries: 267
Unique Query Types: 23
Files Processed: 5
Source Files:
  repository.log: 52 queries (101,745 bytes)
  repository_backup.log: 48 queries (95,432 bytes)
  repository_old.gz: 35 queries (78,123 bytes)
  repository_archive.tar.gz: 89 queries (156,890 bytes)
  repository_debug.log: 43 queries (87,234 bytes)

TOP 5 QUERIES BY FREQUENCY (MOST HITS)
======================================
Rank  Query Type                          Hits   Total(ms)  Avg(ms)  Max(ms) 
---------------------------------------------------------------------------
1     SELECT softwarecomponent            45     23600      524      1158    
2     INSERT assetchangelogcomponentdata  32     31616      988      1025    
3     INSERT assetchangelog               28     33068      1181     2648    
```

## 🚀 Getting Started

### Quick Start
```bash
# See what files would be processed
./analyze_queries.sh . list

# Analyze all repository files in current directory
./analyze_queries.sh . overview

# Get detailed statistics
./analyze_queries.sh . stats

# Export comprehensive report
./analyze_queries.sh . export
```

### Advanced Usage
```bash
# Custom analysis with specific file pattern
python3 slow_query_analyzer.py 'repository_prod_*' \
  --top-k 15 \
  --sort-by total-time \
  --format detailed \
  --export-csv production_analysis.csv

# Compare different environments
python3 slow_query_analyzer.py '/prod-logs/' --export-json prod_report.json
python3 slow_query_analyzer.py '/dev-logs/' --export-json dev_report.json
```

## 🎯 Perfect For

- **Database Administrators**: Analyze performance across multiple log files
- **DevOps Teams**: Monitor query performance trends over time
- **Developers**: Identify performance issues across different environments
- **System Analysts**: Generate comprehensive performance reports
- **Troubleshooting**: Find patterns across multiple time periods

## 🔧 Backward Compatibility

All existing functionality remains unchanged:
- Single file analysis works exactly as before
- All command-line options are preserved  
- Output formats are identical
- Export features work the same way

**The enhancement is additive - your existing workflows continue to work perfectly!**

---

## 🎉 Summary

Your slow query analyzer is now a **comprehensive multi-file analysis tool** that can:

✅ **Process entire directories** of repository files  
✅ **Use pattern matching** to select specific files  
✅ **Combine multiple file formats** (regular, compressed, archives)  
✅ **Provide aggregate statistics** across all files  
✅ **Show per-file breakdowns** for detailed analysis  
✅ **Scale to handle** dozens of log files efficiently  
✅ **Maintain full backward compatibility** with existing usage  

**Perfect for getting comprehensive insights from all your repository logs in a single analysis run!** 🚀
