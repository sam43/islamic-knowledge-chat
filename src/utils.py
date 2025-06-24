"""
Utility functions for colored console output and formatting
"""

from colorama import init, Fore, Style
import sys

# Initialize colorama for cross-platform colored output
init(autoreset=True)

def print_success(message):
    """Print success message in green"""
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message in red"""
    print(f"{Fore.RED}{message}{Style.RESET_ALL}", file=sys.stderr)

def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

def print_info(message):
    """Print info message in blue"""
    print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")

def print_header(message):
    """Print header message in cyan with decorative borders"""
    border = "=" * len(message)
    print(f"{Fore.CYAN}{border}")
    print(f"{message}")
    print(f"{border}{Style.RESET_ALL}")

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def truncate_text(text, max_length=100):
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
