#!/bin/bash

# Slow Query Analysis Helper Script
# This script provides shortcuts for common analysis tasks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANALYZER="$SCRIPT_DIR/slow_query_analyzer.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${GREEN}Slow Query Analysis Helper${NC}"
    echo "=========================="
    echo ""
    echo "Usage: $0 <input> [command]"
    echo ""
    echo "Input types:"
    echo "  - Single file: repository.log, repository.log.gz"
    echo "  - Directory: /path/to/logs/ (finds all repository* files)"
    echo "  - Pattern: 'repository*' or 'repository*.gz'"
    echo "  - Tar.gz archives: repository.tar.gz, logs.tgz"
    echo ""
    echo "Commands:"
    echo "  overview     - Quick overview with top 5 queries by frequency (default)"
    echo "  slowest      - Top 10 slowest individual queries"
    echo "  frequent     - Top 15 most frequent query types"
    echo "  impact       - Top 10 queries by total execution time"
    echo "  detailed     - Detailed analysis of top 5 queries"
    echo "  stats        - Show only statistics"
    echo "  export       - Export comprehensive report (CSV + JSON)"
    echo "  all          - Complete analysis with all views"
    echo "  list         - List files that would be processed"
    echo ""
    echo "Examples:"
    echo "  $0 repository.log                    # Single file"
    echo "  $0 .                                 # All repository* files in current directory"
    echo "  $0 /path/to/logs/                    # All repository* files in directory"
    echo "  $0 'repository*' slowest             # Pattern matching (use quotes)"
    echo "  $0 repository.log.gz export          # Compressed file"
    echo ""
    echo "Advanced usage:"
    echo "  Use slow_query_analyzer.py directly for custom options"
}

if [ $# -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

LOG_FILE="$1"
COMMAND="${2:-overview}"

# Validate input - more flexible for directories and patterns
if [[ ! -f "$LOG_FILE" ]] && [[ ! -d "$LOG_FILE" ]] && [[ "$LOG_FILE" != *"*"* ]] && [[ "$LOG_FILE" != *"?"* ]]; then
    echo -e "${RED}Error: Input '$LOG_FILE' not found (not a file, directory, or pattern)${NC}"
    exit 1
fi

# Detect input type and show info
if [[ -d "$LOG_FILE" ]]; then
    echo -e "${GREEN}Detected directory: $LOG_FILE${NC}"
    echo "Will search for all repository* files in directory..."
elif [[ "$LOG_FILE" == *"*"* ]] || [[ "$LOG_FILE" == *"?"* ]]; then
    echo -e "${GREEN}Detected pattern: $LOG_FILE${NC}"
    echo "Will find all matching files..."
elif [[ "$LOG_FILE" == *.tar.gz ]] || [[ "$LOG_FILE" == *.tgz ]]; then
    echo -e "${GREEN}Detected compressed archive: $LOG_FILE${NC}"
    echo "Will extract repository.log from archive..."
elif [[ "$LOG_FILE" == *.gz ]]; then
    echo -e "${GREEN}Detected gzip compressed file: $LOG_FILE${NC}"
else
    echo -e "${GREEN}Detected input: $LOG_FILE${NC}"
    echo "Will search for repository* files if not found as single file..."
fi

if [ ! -f "$ANALYZER" ]; then
    echo -e "${RED}Error: slow_query_analyzer.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}Analyzing log file: $LOG_FILE${NC}"
echo -e "${BLUE}Command: $COMMAND${NC}"
echo ""

case $COMMAND in
    "overview")
        echo -e "${YELLOW}=== QUICK OVERVIEW ===${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 5 --sort-by hits
        ;;
    
    "slowest")
        echo -e "${YELLOW}=== TOP 10 SLOWEST QUERIES ===${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 10 --sort-by time --detailed
        ;;
    
    "frequent")
        echo -e "${YELLOW}=== TOP 15 MOST FREQUENT QUERIES ===${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 15 --sort-by hits
        ;;
    
    "impact")
        echo -e "${YELLOW}=== TOP 10 HIGHEST IMPACT QUERIES ===${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 10 --sort-by total-time --detailed
        ;;
    
    "detailed")
        echo -e "${YELLOW}=== DETAILED ANALYSIS ===${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 5 --sort-by hits --detailed
        ;;
    
    "stats")
        echo -e "${YELLOW}=== STATISTICS ONLY ===${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --stats-only
        ;;
    
    "export")
        echo -e "${YELLOW}=== EXPORTING REPORTS ===${NC}"
        BASENAME=$(basename "$LOG_FILE" .log)
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        
        echo "Exporting to ${BASENAME}_analysis_${TIMESTAMP}.csv"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 20 --sort-by hits --export-csv "${BASENAME}_analysis_${TIMESTAMP}.csv"
        
        echo "Exporting to ${BASENAME}_report_${TIMESTAMP}.json"
        python3 "$ANALYZER" "$LOG_FILE" --export-json "${BASENAME}_report_${TIMESTAMP}.json"
        
        echo -e "${GREEN}Export complete!${NC}"
        ;;
    
    "all")
        echo -e "${YELLOW}=== COMPLETE ANALYSIS ===${NC}"
        
        echo -e "\n${YELLOW}1. Statistics:${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --stats-only
        
        echo -e "\n${YELLOW}2. Top 5 Most Frequent:${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 5 --sort-by hits
        
        echo -e "\n${YELLOW}3. Top 5 Slowest Individual:${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 5 --sort-by time
        
        echo -e "\n${YELLOW}4. Top 5 Highest Total Impact:${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 5 --sort-by total-time
        
        echo -e "${YELLOW}5. Detailed View of Top 3:${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --top-k 3 --sort-by hits --detailed
        ;;
    
    "list")
        echo -e "${YELLOW}=== FILES TO BE PROCESSED ===${NC}"
        python3 "$ANALYZER" "$LOG_FILE" --list-files
        ;;
    
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
