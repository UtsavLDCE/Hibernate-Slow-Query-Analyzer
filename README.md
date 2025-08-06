# Slow Query Analyzer Package

This package provides comprehensive tools for analyzing slow query logs and identifying database performance bottlenecks.

## 📁 Files Included

- **`slow_query_analyzer.py`** - Main analysis script with full feature set
- **`analyze_queries.sh`** - Simple wrapper script with common shortcuts  
- **`USAGE_GUIDE.md`** - Comprehensive usage documentation
- **`repository_slow_queries_analysis.md`** - Sample analysis report from your data

## 🚀 Quick Start

### Simple Usage (Recommended for beginners)
```bash
# Single file analysis
./analyze_queries.sh repository.log

# Analyze ALL repository files in current directory
./analyze_queries.sh .

# Analyze ALL repository files in specific directory
./analyze_queries.sh /path/to/logs/

# Pattern matching (use quotes)
./analyze_queries.sh 'repository*.gz'

# Compressed archive
./analyze_queries.sh logs_20250806.tar.gz

# Show statistics for all files
./analyze_queries.sh . stats
```

### Advanced Usage
```bash
# Single file analysis
python3 slow_query_analyzer.py repository.log --top-k 10 --sort-by hits

# Analyze ALL repository files in directory
python3 slow_query_analyzer.py /logs/ --top-k 5 --sort-by time --format json

# Pattern matching for specific files
python3 slow_query_analyzer.py 'repository_2025*.gz' --sort-by total-time --detailed

# List files before processing
python3 slow_query_analyzer.py . --list-files

# Export combined results from multiple files
python3 slow_query_analyzer.py . --export-csv combined_analysis.csv
```

## 📊 Analysis Results from Your Data

From your `repository.log` analysis:

### Key Statistics (Single File Example)
- **Total Slow Queries:** 52
- **Unique Query Types:** 20  
- **Files Processed:** 1
- **Total Execution Time:** 32,312ms
- **Average Execution Time:** 621ms
- **Slowest Query:** 2,648ms

### Multi-File Analysis Power
When analyzing multiple repository files:
- **Combines data** from all repository*.log, repository*.gz files
- **Shows aggregate statistics** across all files
- **Identifies patterns** across different time periods
- **Per-file breakdown** in detailed statistics

### Top Performance Issues
1. **SELECT SoftwareComponent** (9 hits, 4,720ms total)
2. **INSERT AssetChangeLogComponentData** (6 hits, 5,927ms total)  
3. **INSERT AssetChangeLog** (5 hits, 5,907ms total)
4. **SELECT SsoConfig** (5 hits, 3,560ms total)

## 🎯 Common Use Cases

### For Database Administrators
```bash
# Find queries that need immediate attention
./analyze_queries.sh myapp.log impact

# Get exportable report for management
./analyze_queries.sh myapp.log export
```

### For Developers
```bash
# Identify most problematic queries during development
./analyze_queries.sh debug.log frequent

# Deep dive into specific slow queries
python3 slow_query_analyzer.py debug.log --sort-by time --detailed
```

### For Performance Monitoring
```bash
# Automated monitoring (returns just statistics)
python3 slow_query_analyzer.py app.log --stats-only

# JSON output for integration with monitoring tools
python3 slow_query_analyzer.py app.log --format json
```

## 📈 Output Formats

### 1. Table Format (Default)
Clean, tabular output perfect for terminal viewing:
```
TOP 5 QUERIES BY FREQUENCY (MOST HITS)
======================================
Rank  Query Type                          Hits   Total(ms)  Avg(ms)  Max(ms) 
---------------------------------------------------------------------------
1     SELECT softwarecomponent            9      4720       524      1158    
```

### 2. Detailed Format
Comprehensive output with query samples:
```
1. SELECT softwarecomponent
   Hits: 9, Total: 4720ms, Avg: 524ms
   Range: 141ms - 1158ms
   Sample: select softwareco0_.id as id1_862_...
```

### 3. JSON Format
Structured data for programmatic use:
```json
{
  "statistics": {
    "total_slow_queries": 52,
    "unique_query_types": 20
  },
  "data": [...]
}
```

## 🔧 Installation & Setup

1. **Make scripts executable:**
   ```bash
   chmod +x slow_query_analyzer.py analyze_queries.sh
   ```

2. **Verify Python 3 is available:**
   ```bash
   python3 --version
   ```

3. **Test with your log files:**
   ```bash
   ./analyze_queries.sh repository.log            # Single file
   ./analyze_queries.sh .                         # All repository* files in current directory
   ./analyze_queries.sh /path/to/logs/            # All repository* files in directory
   ./analyze_queries.sh 'repository_2025*'       # Pattern matching
   ./analyze_queries.sh logs_archive.tar.gz       # Compressed archive
   ```

## 📁 Supported Input Types

The analyzer supports multiple input formats:

### Single Files
- **Regular log files**: `repository.log`, `repository_backup.log`
- **Gzip compressed files**: `repository.log.gz`, `repository_old.gz`
- **Tar.gz archives**: `logs_20250806.tar.gz`, `repository.tar.gz`, `logs.tgz`

### Multi-File Processing
- **Directory scanning**: `/path/to/logs/` (finds all repository* files)
- **Current directory**: `.` (finds all repository* files in current directory)
- **Pattern matching**: `'repository*.gz'`, `'repository_2025*'`
- **Glob patterns**: `'**/repository*.log'`

### Smart File Discovery
The script automatically finds repository files by:
1. **Pattern matching**: `repository*.log`, `repository*.gz`, `repository*.tar.gz`
2. **Directory scanning**: Searches recursively for repository files
3. **Multiple formats**: Combines different file types (regular, compressed, archives)
4. **Duplicate removal**: Ensures each file is processed only once
5. **Sorted processing**: Files processed in consistent order

### Archive Processing
For tar.gz archives, the script will:
1. Automatically search for `repository.log` files inside the archive
2. Handle nested directory structures
3. Extract and process the log file in memory (no temporary files)
4. Support multiple repository.log files (will use the first one found)

## 📝 Log Format Requirements

The analyzer expects log entries in this format:
```
YYYY-MM-DD HH:mm:ss.sss ... SlowQuery: XXX milliseconds. SQL: 'HikariProxyPreparedStatement@... wrapping ACTUAL_SQL_QUERY'
```

This format is standard for:
- Java applications using HikariCP
- Spring Boot applications
- Many enterprise Java frameworks

## 🔍 Analysis Types

| Sort Option | Purpose | Best For |
|-------------|---------|----------|
| `hits` | Most frequent slow queries | Finding queries that slow down the system regularly |
| `time` | Individual slowest queries | Identifying worst-performing individual queries |
| `total-time` | Highest cumulative impact | Understanding overall system impact |

## 📤 Export Options

- **CSV Export:** Perfect for spreadsheet analysis and reporting
- **JSON Export:** Ideal for integration with other tools and automated processing
- **Full Reports:** Comprehensive analysis including all metrics

## 🎨 Wrapper Script Commands

The `analyze_queries.sh` script provides these convenient shortcuts and supports all file types:

| Command | Description |
|---------|-------------|
| `overview` | Quick overview (default) |
| `slowest` | Top 10 slowest individual queries |
| `frequent` | Top 15 most frequent query types |
| `impact` | Top 10 by total execution time |
| `detailed` | Detailed analysis of top queries |
| `stats` | Statistics only |
| `export` | Generate CSV and JSON exports |
| `all` | Complete analysis with all views |
| `list` | List files that would be processed |

## 🔧 Customization

The main script (`slow_query_analyzer.py`) supports extensive customization:

- **Configurable top-k results** (any number)
- **Multiple sorting criteria**
- **Various output formats**
- **Export capabilities**
- **Extensible for different log formats**

## 🚨 Performance Recommendations Based on Your Data

Based on your repository.log analysis, consider:

1. **Index `SoftwareComponent.refId`** - Most queried field (9 hits)
2. **Optimize AssetChangeLog inserts** - Taking up to 2.6 seconds  
3. **Review SsoConfig queries** - Possible full table scans
4. **Consider caching** for frequently accessed configuration data
5. **Analyze complex workflow queries** with multiple JOINs

## 🆘 Troubleshooting

**No slow queries found?**
- Verify log file format matches expected pattern
- Check file permissions and encoding

**Memory issues with large files?**
- Split large log files before analysis
- Process files in chunks if needed

**Want to modify for different log formats?**
- Edit the regex pattern in `slow_query_analyzer.py`
- Adjust the parsing logic for your specific format

## 📞 Support

For questions or issues:
1. Check the `USAGE_GUIDE.md` for detailed documentation
2. Review the sample analysis in `repository_slow_queries_analysis.md`
3. Examine the generated reports for insights

## 🆕 New Features Added

### ✅ Multi-File Processing (NEW!)
The script now supports:
- **Directory scanning**: Analyze ALL repository files at once
- **Pattern matching**: Use glob patterns like `'repository*.gz'`
- **Combined analysis**: Aggregate results from multiple files
- **Smart discovery**: Automatically finds all repository files

### ✅ Compressed File Support
Supports all common formats:
- **Regular files**: `repository.log`
- **Gzip compressed**: `repository.log.gz` 
- **Tar.gz archives**: `logs_20250806.tar.gz`, `backup.tgz`

### ✅ Smart Archive Processing
- Automatically finds `repository.log` files in archives
- Handles nested directory structures
- Memory-efficient (no temporary files)
- Supports multiple repository.log files in one archive

### ✅ Enhanced Error Handling
- Graceful handling of compressed file errors
- Better user feedback during extraction
- Cleanup of resources

## 🎯 Complete Feature List

- ✅ **Multi-file processing**: Analyze multiple repository files in one run
- ✅ **Directory scanning**: Process all repository files in a directory
- ✅ **Pattern matching**: Use glob patterns to select specific files
- ✅ **Multi-format support**: Regular, .gz, .tar.gz, .tgz files
- ✅ **Configurable analysis**: Sort by hits, time, or total impact
- ✅ **Multiple output formats**: Table, detailed, JSON
- ✅ **Export capabilities**: CSV and JSON reports
- ✅ **Smart parsing**: Automatically categorizes queries by operation and table
- ✅ **Comprehensive statistics**: Full performance metrics with per-file breakdown
- ✅ **User-friendly wrapper**: Simple commands for common tasks
- ✅ **Archive intelligence**: Finds logs in compressed archives
- ✅ **Memory efficient**: Processes large files without temporary storage
- ✅ **Error resilient**: Handles encoding and compression issues gracefully
- ✅ **File discovery**: Lists files before processing with --list-files option

---

**Happy analyzing! 🎉**

This enhanced toolkit now supports all common log file formats and should help you identify and resolve database performance issues efficiently, whether your logs are in regular files, compressed archives, or nested directory structures.
