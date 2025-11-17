"""
Queue manager for batch downloads.
Handles multiple URLs in a queue with pause/resume/cancel.
"""
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List, Optional, Callable
from pathlib import Path


class DownloadState(Enum):
    """State of a download item."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadItem:
    """Single item in download queue."""
    url: str
    state: DownloadState = DownloadState.PENDING
    progress: int = 0
    status_text: str = ""
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __str__(self):
        return f"[{self.state.value.upper()}] {self.url} ({self.progress}%)"


class QueueManager:
    """Manage a queue of downloads."""
    
    def __init__(self):
        self.items: List[DownloadItem] = []
        self.is_paused = False
        self.current_index = 0
    
    def add_url(self, url: str) -> bool:
        """Add a URL to the queue.
        
        Args:
            url: URL to add.
            
        Returns:
            True if added, False if duplicate or invalid.
        """
        url = url.strip()
        
        # Check for duplicates
        if any(item.url == url for item in self.items):
            return False
        
        self.items.append(DownloadItem(url=url))
        return True
    
    def add_urls(self, urls: List[str]) -> int:
        """Add multiple URLs to the queue.
        
        Args:
            urls: List of URLs to add.
            
        Returns:
            Number of URLs actually added.
        """
        count = 0
        for url in urls:
            if self.add_url(url):
                count += 1
        return count
    
    def remove_item(self, index: int) -> bool:
        """Remove an item from the queue.
        
        Args:
            index: Index of item to remove.
            
        Returns:
            True if removed, False if index invalid.
        """
        if 0 <= index < len(self.items):
            del self.items[index]
            if self.current_index >= len(self.items):
                self.current_index = max(0, len(self.items) - 1)
            return True
        return False
    
    def clear(self):
        """Clear all items from queue."""
        self.items.clear()
        self.current_index = 0
    
    def get_current(self) -> Optional[DownloadItem]:
        """Get current item being downloaded."""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]
        return None
    
    def next(self) -> Optional[DownloadItem]:
        """Move to next item in queue."""
        self.current_index += 1
        return self.get_current()
    
    def update_current(self, progress: int, status: str):
        """Update progress of current item."""
        item = self.get_current()
        if item:
            item.progress = progress
            item.status_text = status
            if item.state == DownloadState.PENDING:
                item.state = DownloadState.DOWNLOADING
                item.started_at = datetime.now()
    
    def mark_current_completed(self):
        """Mark current item as completed."""
        item = self.get_current()
        if item:
            item.state = DownloadState.COMPLETED
            item.completed_at = datetime.now()
    
    def mark_current_failed(self, error: str):
        """Mark current item as failed."""
        item = self.get_current()
        if item:
            item.state = DownloadState.FAILED
            item.error = error
            item.completed_at = datetime.now()
    
    def pause(self):
        """Pause queue processing."""
        self.is_paused = True
    
    def resume(self):
        """Resume queue processing."""
        self.is_paused = False
    
    def cancel_current(self):
        """Cancel current download."""
        item = self.get_current()
        if item:
            item.state = DownloadState.CANCELLED
            item.completed_at = datetime.now()
    
    def get_stats(self) -> dict:
        """Get queue statistics."""
        total = len(self.items)
        completed = sum(1 for i in self.items if i.state == DownloadState.COMPLETED)
        failed = sum(1 for i in self.items if i.state == DownloadState.FAILED)
        pending = sum(1 for i in self.items if i.state == DownloadState.PENDING)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "current_index": self.current_index,
        }
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.items) == 0
    
    def has_next(self) -> bool:
        """Check if there's a next item."""
        return self.current_index + 1 < len(self.items)
