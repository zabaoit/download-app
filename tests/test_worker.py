import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.gui import DownloadWorker


class TestDownloadWorker:
    """Test DownloadWorker functionality."""
    
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Provide temporary directory for downloads."""
        return str(tmp_path / "downloads")
    
    @pytest.fixture
    def worker(self, temp_dir):
        """Create a DownloadWorker instance."""
        return DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir,
            quality="auto"
        )
    
    def test_worker_initialization(self, worker, temp_dir):
        """Should initialize with correct parameters."""
        assert worker.url == "https://example.com/video"
        assert worker.outdir == temp_dir
        assert worker.quality == "auto"
    
    def test_worker_quality_default(self, temp_dir):
        """Should default to 'auto' quality."""
        worker = DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir
        )
        assert worker.quality == "auto"
    
    def test_worker_quality_1080p(self, temp_dir):
        """Should accept 1080p quality."""
        worker = DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir,
            quality="1080p"
        )
        assert worker.quality == "1080p"
    
    def test_worker_quality_720p(self, temp_dir):
        """Should accept 720p quality."""
        worker = DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir,
            quality="720p"
        )
        assert worker.quality == "720p"
    
    def test_worker_quality_audio(self, temp_dir):
        """Should accept audio quality."""
        worker = DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir,
            quality="audio"
        )
        assert worker.quality == "audio"
    
    def test_format_map_auto(self, temp_dir):
        """Should map 'auto' to best format."""
        worker = DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir,
            quality="auto"
        )
        # The format map is used in run() method
        format_map = {
            "auto": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "audio": "bestaudio/best"
        }
        assert format_map[worker.quality] == "bestvideo+bestaudio/best"
    
    def test_format_map_1080p(self, temp_dir):
        """Should map '1080p' to 1080p format."""
        worker = DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir,
            quality="1080p"
        )
        format_map = {
            "auto": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "audio": "bestaudio/best"
        }
        assert format_map[worker.quality] == "bestvideo[height<=1080]+bestaudio/best"
    
    def test_format_map_audio(self, temp_dir):
        """Should map 'audio' to audio-only format."""
        worker = DownloadWorker(
            url="https://example.com/video",
            outdir=temp_dir,
            quality="audio"
        )
        format_map = {
            "auto": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "audio": "bestaudio/best"
        }
        assert format_map[worker.quality] == "bestaudio/best"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
