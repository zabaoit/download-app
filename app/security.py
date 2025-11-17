"""
Security utilities for Download App.
Includes filename sanitization and URL validation.
"""
import re
import urllib.parse
from pathlib import Path


INVALID_CHARS_PATTERN = re.compile(r'[<>:"|?*\x00-\x1f]')
INVALID_FILENAMES = {
    "con", "prn", "aux", "nul",
    "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
    "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
}


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize a filename to be safe for filesystem.
    
    Args:
        filename: Original filename.
        max_length: Maximum length for the filename (default 255 for most filesystems).
        
    Returns:
        Sanitized filename.
    """
    # Remove invalid characters
    sanitized = INVALID_CHARS_PATTERN.sub("_", filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")
    
    # Handle reserved names (Windows)
    name_without_ext = sanitized.rsplit(".", 1)[0].lower()
    if name_without_ext in INVALID_FILENAMES:
        sanitized = "_" + sanitized
    
    # Ensure not empty
    if not sanitized:
        sanitized = "download"
    
    # Truncate if too long
    if len(sanitized) > max_length:
        # Try to preserve extension
        parts = sanitized.rsplit(".", 1)
        if len(parts) == 2:
            name, ext = parts
            max_name = max_length - len(ext) - 1
            sanitized = name[:max_name] + "." + ext
        else:
            sanitized = sanitized[:max_length]
    
    return sanitized


def validate_url(url: str) -> bool:
    """Validate if URL is a proper web URL.
    
    Args:
        url: URL string to validate.
        
    Returns:
        True if URL is valid, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # Check if it starts with http/https
    if not (url.startswith("http://") or url.startswith("https://")):
        # Try to parse as is (some platforms might have custom schemes)
        return False
    
    try:
        result = urllib.parse.urlparse(url)
        # Must have scheme and netloc (domain)
        return bool(result.scheme and result.netloc)
    except Exception:
        return False


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """Check if target path is within base_dir (prevent path traversal).
    
    Args:
        base_dir: Base directory (safe zone).
        target_path: Target path to check.
        
    Returns:
        True if target is within base_dir, False otherwise.
    """
    try:
        base_dir = base_dir.resolve()
        target_path = target_path.resolve()
        # Check if target is relative to base
        target_path.relative_to(base_dir)
        return True
    except ValueError:
        return False
