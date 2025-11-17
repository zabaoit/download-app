import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.security import sanitize_filename, validate_url, is_safe_path


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    def test_removes_invalid_characters(self):
        """Should replace invalid characters with underscore."""
        assert sanitize_filename('file<name>.txt') == 'file_name_.txt'
        assert sanitize_filename('file"name".txt') == 'file_name_.txt'
        assert sanitize_filename('file:name.txt') == 'file_name.txt'
        assert sanitize_filename('file|name.txt') == 'file_name.txt'
        assert sanitize_filename('file?name.txt') == 'file_name.txt'
        assert sanitize_filename('file*name.txt') == 'file_name.txt'
    
    def test_handles_windows_reserved_names(self):
        """Should handle Windows reserved names by prepending underscore."""
        assert sanitize_filename('CON') == '_CON'
        assert sanitize_filename('con.txt') == '_con.txt'
        assert sanitize_filename('PRN') == '_PRN'
        assert sanitize_filename('AUX') == '_AUX'
        assert sanitize_filename('NUL') == '_NUL'
    
    def test_truncates_long_filenames(self):
        """Should truncate filenames longer than 255 chars."""
        long_name = 'a' * 300 + '.txt'
        result = sanitize_filename(long_name)
        assert len(result) <= 255
    
    def test_preserves_valid_names(self):
        """Should preserve valid filenames."""
        assert sanitize_filename('my-video_2024.mp4') == 'my-video_2024.mp4'
        assert sanitize_filename('hello world.txt') == 'hello world.txt'
    
    def test_handles_empty_string(self):
        """Should handle empty string."""
        result = sanitize_filename('')
        assert result is not None


class TestValidateUrl:
    """Test URL validation."""
    
    def test_accepts_http_urls(self):
        """Should accept http URLs."""
        assert validate_url('http://example.com/video') == True
    
    def test_accepts_https_urls(self):
        """Should accept https URLs."""
        assert validate_url('https://example.com/video') == True
    
    def test_rejects_ftp_urls(self):
        """Should reject ftp URLs."""
        assert validate_url('ftp://example.com/file') == False
    
    def test_rejects_malformed_urls(self):
        """Should reject malformed URLs."""
        assert validate_url('not a url') == False
        assert validate_url('example.com') == False
    
    def test_rejects_empty_url(self):
        """Should reject empty URL."""
        assert validate_url('') == False
    
    def test_accepts_youtube_urls(self):
        """Should accept YouTube URLs."""
        assert validate_url('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == True
    
    def test_accepts_url_with_query_params(self):
        """Should accept URLs with query parameters."""
        assert validate_url('https://example.com/video?id=123&format=mp4') == True


class TestIsSafePath:
    """Test path safety checking."""
    
    def test_accepts_valid_paths(self):
        """Should accept valid paths."""
        test_path = Path.home() / 'downloads' / 'video.mp4'
        # is_safe_path(base_dir, target_path)
        result = is_safe_path(Path.home() / 'downloads', test_path)
        assert result == True
    
    def test_rejects_path_traversal(self):
        """Should reject path traversal attempts."""
        base = Path.home() / 'downloads'
        unsafe = base / '..' / '..' / 'etc' / 'passwd'
        result = is_safe_path(base, unsafe)
        assert result == False
    
    def test_rejects_absolute_paths_outside_base(self):
        """Should reject absolute paths outside base directory."""
        base = Path.home() / 'downloads'
        outside = Path('/etc/passwd')
        result = is_safe_path(base, outside)
        assert result == False
    
    def test_accepts_nested_valid_paths(self):
        """Should accept nested paths within base."""
        base = Path.home() / 'downloads'
        valid = base / 'subfolder' / 'video.mp4'
        result = is_safe_path(base, valid)
        assert result == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
