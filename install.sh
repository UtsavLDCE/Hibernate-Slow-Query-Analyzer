#!/bin/bash

# Slow Query Analyzer Installation Script
# ========================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

INSTALL_DIR="$HOME/bin"
PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}Slow Query Analyzer Package Installation${NC}"
echo "========================================="
echo ""

# Check Python 3
echo -e "${YELLOW}Checking Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}✓ Python 3 found: $PYTHON_VERSION${NC}"

# Check required Python modules
echo -e "${YELLOW}Checking required Python modules...${NC}"
python3 -c "import re, sys, json, argparse, tarfile, gzip, os, tempfile, glob, csv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All required Python modules are available${NC}"
else
    echo -e "${RED}Error: Some required Python modules are missing.${NC}"
    echo "Required modules: re, sys, json, argparse, tarfile, gzip, os, tempfile, glob, csv"
    exit 1
fi

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Creating installation directory: $INSTALL_DIR${NC}"
    mkdir -p "$INSTALL_DIR"
fi

# Add to PATH if not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}Adding $INSTALL_DIR to PATH...${NC}"
    
    # Add to appropriate shell configuration file
    SHELL_CONFIG=""
    if [ -n "$BASH_VERSION" ] && [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_CONFIG"
        echo -e "${GREEN}✓ Added to $SHELL_CONFIG${NC}"
        echo -e "${YELLOW}Note: You may need to restart your shell or run 'source $SHELL_CONFIG'${NC}"
    else
        echo -e "${YELLOW}Warning: Could not determine shell configuration file.${NC}"
        echo -e "${YELLOW}Please manually add $INSTALL_DIR to your PATH.${NC}"
    fi
fi

# Copy files
echo -e "${YELLOW}Installing files...${NC}"

# Install main script
cp "$PACKAGE_DIR/slow_query_analyzer.py" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/slow_query_analyzer.py"
echo -e "${GREEN}✓ Installed slow_query_analyzer.py${NC}"

# Install wrapper script
cp "$PACKAGE_DIR/analyze_queries.sh" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/analyze_queries.sh"
echo -e "${GREEN}✓ Installed analyze_queries.sh${NC}"

# Create convenient symlinks
ln -sf "$INSTALL_DIR/slow_query_analyzer.py" "$INSTALL_DIR/analyze-queries"
ln -sf "$INSTALL_DIR/analyze_queries.sh" "$INSTALL_DIR/quick-query-analysis"
echo -e "${GREEN}✓ Created convenient command aliases${NC}"

# Copy documentation to a docs directory
DOC_DIR="$HOME/.local/share/slow-query-analyzer"
mkdir -p "$DOC_DIR"
cp "$PACKAGE_DIR"/*.md "$DOC_DIR/"
cp -r "$PACKAGE_DIR/examples" "$DOC_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Installed documentation to $DOC_DIR${NC}"

echo ""
echo -e "${GREEN}Installation completed successfully! 🎉${NC}"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo "  analyze_queries.sh repository.log"
echo "  analyze_queries.sh . --all"
echo "  slow_query_analyzer.py /logs/ --export-csv report.csv"
echo "  analyze-queries repository.log  # Alternative command"
echo "  quick-query-analysis .          # Quick wrapper"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  View help: analyze_queries.sh --help"
echo "  Full docs:  ls $DOC_DIR/"
echo ""

# Test installation
echo -e "${YELLOW}Testing installation...${NC}"
if command -v analyze_queries.sh &> /dev/null; then
    echo -e "${GREEN}✓ Commands available in PATH${NC}"
else
    echo -e "${YELLOW}! Commands not yet in PATH. You may need to restart your shell.${NC}"
fi

echo ""
echo -e "${GREEN}Ready to analyze your slow queries! 🚀${NC}"
