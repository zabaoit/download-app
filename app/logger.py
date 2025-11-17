"""
Logging configuration for Download App.
Sets up file and console logging.
"""
import logging
from pathlib import Path
from datetime import datetime


def setup_logging(log_dir: Path = None) -> logging.Logger:
    """Configure logging to file and console.
    
    Args:
        log_dir: Directory to store logs. Defaults to current directory/logs.
        
    Returns:
        Configured logger instance.
    """
    if log_dir is None:
        log_dir = Path.cwd() / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("download_app")
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler (debug level, verbose format)
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Console handler (warning level, concise format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_format = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "download_app") -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
