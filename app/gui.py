from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QComboBox,
)
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor
import yt_dlp
from pathlib import Path
import subprocess
import os
import sys
import shutil
import re
from .settings import SettingsManager
from .logger import setup_logging, get_logger
from .security import validate_url, sanitize_filename


class DownloadWorker(QObject):
    progress = Signal(int, str)  # percent, status text
    finished = Signal(bool, str)  # success, message/path

    def __init__(self, url: str, outdir: str, quality: str = "auto"):
        super().__init__()
        self.url = url
        self.outdir = outdir
        self.quality = quality  # "auto", "1080p", "720p", "audio"
        self._last_percent = 0
        self._last_filename = None
        self.logger = get_logger("DownloadWorker")

    def _detect_hevc(self, video_path: str) -> bool:
        """Detect if video uses HEVC codec using ffmpeg output."""
        try:
            # Find ffmpeg executable
            ffmpeg_cmd = shutil.which("ffmpeg")
            if not ffmpeg_cmd:
                if getattr(sys, "frozen", False):
                    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
                    candidate = base / "ffmpeg.exe"
                    if candidate.exists():
                        ffmpeg_cmd = str(candidate)
                else:
                    candidate = Path(__file__).resolve().parents[1] / "ffmpeg" / "ffmpeg.exe"
                    if candidate.exists():
                        ffmpeg_cmd = str(candidate)

            if not ffmpeg_cmd:
                self.logger.warning("ffmpeg not found; cannot detect HEVC codec")
                return False

            # Use ffmpeg to probe video (parse output for hevc/h265/hvc1)
            try:
                result = subprocess.run(
                    [ffmpeg_cmd, "-i", video_path],
                    capture_output=True,
                    text=False,  # Get bytes, not text (avoid encoding issues)
                    timeout=10,
                )
                # Decode with error handling (ignore non-UTF8 chars)
                try:
                    output = result.stdout.decode('utf-8', errors='ignore') + result.stderr.decode('utf-8', errors='ignore')
                except:
                    output = ""
                
                is_hevc = "hevc" in output.lower() or "h265" in output.lower() or "hvc1" in output.lower()
                self.logger.info(f"Video codec check: HEVC={is_hevc}")
                return is_hevc
            except subprocess.TimeoutExpired:
                self.logger.warning("Timeout detecting HEVC codec")
                return False
        except Exception as e:
            self.logger.warning(f"Error detecting HEVC codec: {e}")
            return False

    def _progress_hook(self, d):
        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                try:
                    percent = int(downloaded * 100 / total)
                except Exception:
                    percent = 0
            else:
                percent = 0
            eta = d.get("eta")
            text = f"Đang tải... {percent}% (ETA: {eta}s)" if eta is not None else f"Đang tải... {percent}%"
            # throttle signals if percent hasn't changed to avoid UI spam
            if percent != self._last_percent:
                self._last_percent = percent
                self.progress.emit(percent, text)
        elif status == "finished":
            filename = d.get("filename") or ""
            # remember downloaded filename for post-processing
            self._last_filename = filename
            # Do NOT emit a UI progress update here — conversion will run
            # and the UI will be updated once everything (including conversion) completes.

    @Slot()
    def run(self):
        try:
            # Sanitize output template to prevent path traversal
            sanitized_title = sanitize_filename("%(title)s")
            outtmpl = str(Path(self.outdir) / f"{sanitized_title}.%(ext)s")
            
            # Set format based on quality setting
            format_map = {
                "auto": "best[ext=mp4]/best",
                "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio/best",
                "720p": "bestvideo[height<=720][ext=mp4]+bestaudio/best",
                "audio": "bestaudio/best",
            }
            
            ydl_opts = {
                "outtmpl": outtmpl,
                "progress_hooks": [self._progress_hook],
                "format": format_map.get(self.quality, format_map["auto"]),
                "quiet": False,
                "no_warnings": False,
            }
            
            self.logger.info(f"Starting download: {self.url} (quality: {self.quality})")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            final_path = None
            if self._last_filename:
                src = Path(self._last_filename)
                # ensure absolute path
                if not src.is_absolute():
                    src = Path(self.outdir) / src.name

                if src.exists():
                    final_path = str(src)
                    
                    # Check if we should transcode this video
                    should_transcode = self._detect_hevc(str(src))
                    
                    if should_transcode:
                        # Auto-transcode HEVC to H.264 for Windows compatibility
                        tmp = src.with_suffix('.tmp.mp4')
                        try:
                            self.progress.emit(0, "Chuyển đổi video sang định dạng H.264 (tương thích Windows)...")
                            self.logger.info(f"Transcoding HEVC to H.264: {src.name}")

                            # Determine ffmpeg executable: prefer bundled ffmpeg in frozen app or project, fallback to PATH
                            ffmpeg_cmd = shutil.which("ffmpeg")
                            if not ffmpeg_cmd:
                                # If running as PyInstaller bundle, look in _MEIPASS
                                if getattr(sys, "frozen", False):
                                    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
                                    candidate = base / "ffmpeg.exe"
                                    if candidate.exists():
                                        ffmpeg_cmd = str(candidate)
                                else:
                                    # look for app/ffmpeg/ffmpeg.exe in source tree
                                    candidate = Path(__file__).resolve().parents[1] / "ffmpeg" / "ffmpeg.exe"
                                    if candidate.exists():
                                        ffmpeg_cmd = str(candidate)

                            if not ffmpeg_cmd:
                                # If ffmpeg is not found, log and skip transcode (keep original)
                                self.logger.warning("ffmpeg not found; skipping HEVC transcode and keeping original file.")
                            else:
                                # Transcode HEVC to H.264 + AAC for maximum Windows compatibility
                                subprocess.run([
                                    ffmpeg_cmd,
                                    "-y",
                                    "-i",
                                    str(src),
                                    "-c:v",
                                    "libx264",
                                    "-preset",
                                    "medium",  # medium quality/speed balance
                                    "-crf",
                                    "20",  # quality (lower = better, 0-51)
                                    "-c:a",
                                    "aac",
                                    "-b:a",
                                    "192k",
                                    str(tmp),
                                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                                # atomically replace original with tmp
                                try:
                                    tmp.replace(src)
                                    final_path = str(src)
                                    self.logger.info(f"HEVC to H.264 transcode complete: {src}")
                                except Exception:
                                    try:
                                        # fallback to os.replace
                                        os.replace(str(tmp), str(src))
                                        final_path = str(src)
                                        self.logger.info(f"HEVC to H.264 transcode complete (via os.replace): {src}")
                                    except Exception as e:
                                        # if replace fails, keep tmp as final
                                        final_path = str(tmp)
                                        self.logger.warning(f"Could not replace original, using temp file: {e}")
                        except subprocess.CalledProcessError as e:
                            # ffmpeg failed — keep original
                            self.logger.error(f"FFmpeg HEVC transcode failed: {e}")
                            final_path = str(src)
                        except Exception as e:
                            self.logger.error(f"Unexpected error during HEVC transcode: {e}")
                            final_path = str(src)
                    else:
                        # Video is not HEVC; no transcode needed
                        final_path = str(src)
                        self.logger.info(f"Video is not HEVC; keeping original: {src}")
                else:
                    final_path = str(Path(self.outdir))
            else:
                final_path = str(Path(self.outdir))

            self.finished.emit(True, final_path)
        except Exception as e:
            self.logger.error(f"Download failed: {e}", exc_info=True)
            self.finished.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Setup logging
        self.logger = setup_logging()
        self.logger.info("Starting Download App")
        
        self.setWindowTitle("📥 Download Video Đa Nền Tảng")
        
        # Load settings
        self.settings = SettingsManager()
        settings_data = self.settings.load()
        
        # Restore window geometry
        win_x = settings_data.get("window_x", 100)
        win_y = settings_data.get("window_y", 100)
        win_w = settings_data.get("window_width", 700)
        win_h = settings_data.get("window_height", 280)
        self.setGeometry(win_x, win_y, win_w, win_h)
        
        # Load dark mode preference
        self.dark_mode = settings_data.get("dark_mode", False)
        self.setStyleSheet(self._get_stylesheet())
        # Set window icon using emoji/text (fallback for Windows)
        self.setWindowIcon(self._create_icon())

        # Load downloads directory from settings or use default
        downloads_path = settings_data.get("downloads_dir")
        if downloads_path:
            self.downloads_dir = Path(downloads_path)
        else:
            self.downloads_dir = Path(__file__).resolve().parents[1] / "downloads"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

        main_layout = QVBoxLayout()

        # URL input + choose folder row
        row1 = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Nhập URL video...")
        self.url_input.returnPressed.connect(self.start_download)  # trigger download on Enter
        row1.addWidget(self.url_input)

        self.choose_btn = QPushButton("📁 Chọn thư mục")
        self.choose_btn.clicked.connect(self.choose_folder)
        row1.addWidget(self.choose_btn)

        # small icon button for dark mode next to the choose folder button
        self.theme_btn = QPushButton("☀️")
        self.theme_btn.setToolTip("Bật/Tắt Dark Mode")
        self.theme_btn.setCheckable(True)
        self.theme_btn.setFixedSize(36, 28)
        self.theme_btn.clicked.connect(lambda: self._toggle_dark_mode(self.theme_btn.isChecked()))
        row1.addWidget(self.theme_btn)
        
        # Quality selector dropdown
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Auto (Tốt nhất)", "1080p", "720p", "Audio Only"])
        self.quality_combo.setToolTip("Chọn chất lượng video")
        self.quality_combo.setMaximumWidth(150)
        # Restore quality preference from settings
        saved_quality = settings_data.get("quality", "Auto (Tốt nhất)")
        quality_index = self.quality_combo.findText(saved_quality)
        if quality_index >= 0:
            self.quality_combo.setCurrentIndex(quality_index)
        row1.addWidget(self.quality_combo)

        main_layout.addLayout(row1)

        # show selected folder
        header_row = QHBoxLayout()
        self.folder_label = QLabel(f"📂 Lưu vào: {self.downloads_dir}")
        header_row.addWidget(self.folder_label)
        header_row.addStretch()

        main_layout.addLayout(header_row)

        # progress bar and status
        self.progress_bar = QProgressBar()
        # Initially hide progress (no 0% shown). It will appear as a busy indicator when download starts.
        self.progress_bar.setVisible(False)
        # Ensure determinate range default
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)

        self.result_label = QLabel("")
        main_layout.addWidget(self.result_label)

        # buttons
        btn_row = QHBoxLayout()
        self.download_btn = QPushButton("⬇️ Download")
        self.download_btn.clicked.connect(self.start_download)
        btn_row.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("✕ Hủy")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        btn_row.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_row)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # theme state: default light (black & white). Will be toggled by UI.
        self.dark_mode = False

        # worker/thread refs
        self._worker = None
        self._thread = None

    def _create_icon(self):
        """Create a simple icon for the application window."""
        # Create a simple colored square icon (blue background with download symbol)
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(33, 150, 243))  # Material Blue
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))  # White text
        painter.setFont(painter.font())
        painter.drawText(pixmap.rect(), 0x0004, "⬇")  # Down arrow
        painter.end()
        return QIcon(pixmap)

    def _toggle_dark_mode(self, checked: bool):
        # Toggle internal flag and update stylesheet
        self.dark_mode = bool(checked)
        # Update button icon to reflect state
        try:
            if self.dark_mode:
                # show moon when dark mode is active
                self.theme_btn.setText("🌙")
            else:
                # show sun when light mode is active
                self.theme_btn.setText("☀️")
        except Exception:
            pass

        # Apply new stylesheet (full invert of colors when dark_mode True)
        try:
            self.setStyleSheet(self._get_stylesheet())
        except Exception:
            pass
        
        # Save to settings
        self.settings.set("dark_mode", self.dark_mode)

    def choose_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu", str(self.downloads_dir))
        if path:
            self.downloads_dir = Path(path)
            self.folder_label.setText(f"Lưu vào: {self.downloads_dir}")
            # Save to settings
            self.settings.set("downloads_dir", str(self.downloads_dir))

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.result_label.setText("Hãy nhập URL.")
            self.logger.warning("Download attempted with empty URL")
            return
        
        # Validate URL
        if not validate_url(url):
            self.result_label.setText("URL không hợp lệ. Vui lòng nhập đúng URL.")
            self.logger.warning(f"Invalid URL: {url}")
            QMessageBox.warning(
                self,
                "URL Không Hợp Lệ",
                "URL phải bắt đầu bằng http:// hoặc https://",
                QMessageBox.Ok
            )
            return

        # Quick heuristic: detect obvious non-video URLs (TikTok photo posts, direct images)
        lower = url.lower()
        # common image file extensions
        image_exts = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        if any(lower.endswith(ext) for ext in image_exts):
            self.result_label.setText("URL trỏ tới hình ảnh chứ không phải video.")
            QMessageBox.information(self, "Không phải video", "URL này trỏ tới một ảnh (không phải video). Vui lòng dán link video.")
            self.logger.info(f"Blocked image URL: {url}")
            return

        # TikTok photo posts have '/photo/' in path; catch them early to avoid yt-dlp errors
        if 'tiktok.com' in lower and '/photo/' in lower:
            self.result_label.setText("URL TikTok này là bài ảnh, không phải video.")
            QMessageBox.information(self, "Không phải video", "Link TikTok này là bài đăng ảnh (photo), không thể tải video từ link này. Vui lòng dán link video.")
            self.logger.info(f"Blocked TikTok photo URL: {url}")
            return

        # disable buttons while downloading
        self.download_btn.setEnabled(False)
        self.choose_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        # Show a busy/indeterminate progress bar to indicate loading (no 0% shown)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # indeterminate (busy) mode
        self.result_label.setText("Bắt đầu tải...")
        self.logger.info(f"Starting download for: {url}")

        # setup worker in a QThread
        self._thread = QThread()
        # Map UI combo text to quality values
        quality_map = {
            "Auto (Tốt nhất)": "auto",
            "1080p": "1080p",
            "720p": "720p",
            "Audio Only": "audio"
        }
        selected_quality = self.quality_combo.currentText()
        quality_value = quality_map.get(selected_quality, "auto")
        # Save quality preference
        self.settings.set("quality", selected_quality)
        self._worker = DownloadWorker(url, str(self.downloads_dir), quality_value)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._thread.start()

    def cancel_download(self):
        # Terminate thread (not graceful but works)
        if self._thread and self._thread.isRunning():
            self._thread.requestInterruption()
            self._thread.quit()
            self._thread.wait(1000)
        # Call cleanup if available, otherwise perform inline cleanup
        if hasattr(self, "_cleanup_after_cancel"):
            self._cleanup_after_cancel()
        else:
            try:
                self.download_btn.setEnabled(True)
                self.choose_btn.setEnabled(True)
                self.cancel_btn.setEnabled(False)
            except Exception:
                pass
            try:
                self._worker = None
                self._thread = None
            except Exception:
                pass
            try:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                self.progress_bar.setVisible(False)
            except Exception:
                pass

    def _on_progress(self, percent: int, text: str):
        # If percent is 0, keep showing busy indicator (no 0% displayed)
        if percent <= 0:
            # ensure indeterminate mode while initial/convert stages
            if not (self.progress_bar.minimum() == 0 and self.progress_bar.maximum() == 0):
                self.progress_bar.setRange(0, 0)
                self.progress_bar.setVisible(True)
            self.result_label.setText(text)
            return

        # If we receive a real percent (>0) and progress bar was indeterminate, switch to determinate mode
        if self.progress_bar.maximum() == 0:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setVisible(True)

        self.progress_bar.setValue(percent)
        self.result_label.setText(text)

    def _on_finished(self, success: bool, message: str):
        if success:
            self.result_label.setText(f"Tải thành công! Lưu tại: {message}")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.url_input.clear()  # Clear input after successful download
            self.logger.info(f"Download completed: {message}")
        else:
            # Strip ANSI escape sequences from yt-dlp error output
            try:
                clean_message = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', str(message))
            except Exception:
                clean_message = str(message)

            # Friendly message for unsupported URLs
            if "Unsupported URL" in clean_message or "UnsupportedError" in clean_message:
                user_msg = (
                    "URL này không được hỗ trợ (không phải video hoặc nền tảng không được hỗ trợ).\n"
                    "Vui lòng thử một URL video hợp lệ (ví dụ YouTube) hoặc cập nhật yt-dlp.\n\n"
                    f"Chi tiết: {clean_message}"
                )
                self.result_label.setText("Lỗi: URL không được hỗ trợ.")
                self.logger.error(f"Download error: {clean_message}")
                QMessageBox.critical(self, "Lỗi Tải", user_msg, QMessageBox.Ok)
            else:
                # Generic error
                user_msg = f"Tải video thất bại:\n\n{clean_message}\n\nVui lòng kiểm tra URL hoặc thử lại."
                self.result_label.setText(f"Lỗi: {clean_message}")
                self.logger.error(f"Download error: {clean_message}")
                QMessageBox.critical(self, "Lỗi Tải", user_msg, QMessageBox.Ok)

        # cleanup thread/worker
        if self._thread:
            self._thread.quit()
            self._thread.wait()
        # Call cleanup if available, otherwise perform inline cleanup
        if hasattr(self, "_cleanup_after_cancel"):
            self._cleanup_after_cancel()
        else:
            try:
                self.download_btn.setEnabled(True)
                self.choose_btn.setEnabled(True)
                self.cancel_btn.setEnabled(False)
            except Exception:
                pass
            try:
                self._worker = None
                self._thread = None
            except Exception:
                pass
            try:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                self.progress_bar.setVisible(False)
            except Exception:
                pass

    def _cleanup_after_cancel(self):
        """Restore UI state after a download finishes or is cancelled."""
        try:
            # Re-enable primary buttons
            self.download_btn.setEnabled(True)
            self.choose_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
        except Exception:
            pass

        # Clear worker/thread references
        try:
            self._worker = None
            self._thread = None
        except Exception:
            pass

        # Reset and hide progress bar
        try:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(False)
        except Exception:
            pass

    def closeEvent(self, event):
        """Save window geometry when closing."""
        try:
            geometry = self.geometry()
            self.settings.update({
                "window_width": geometry.width(),
                "window_height": geometry.height(),
                "window_x": geometry.x(),
                "window_y": geometry.y(),
            })
        except Exception:
            pass
        event.accept()
        self.download_btn.setEnabled(True)
        self.choose_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None
        self._thread = None
        # reset progress bar to hidden and determinate default
        try:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(False)
        except Exception:
            pass

    def _get_stylesheet(self) -> str:
        """Return modern stylesheet for the application."""
        # Full light/dark styles (invert backgrounds and text)
        if getattr(self, "dark_mode", False):
            # Dark mode: dark backgrounds, light text
            return """
                QMainWindow {
                    background-color: #121212;
                }
                QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 2px solid #2c2c2c;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    selection-background-color: #ffffff;
                    selection-color: #000000;
                }
                QLineEdit::placeholder {
                    color: #9e9e9e;
                }
                QLineEdit:focus {
                    border: 2px solid #ffffff;
                    outline: none;
                }
                QPushButton {
                    background-color: #2c2c2c;
                    color: #ffffff;
                    border: 1px solid #3a3a3a;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:pressed {
                    background-color: #232323;
                }
                QPushButton:disabled {
                    background-color: #2c2c2c;
                    color: #777777;
                }
                QLabel {
                    color: #e0e0e0;
                    font-size: 12px;
                }
                QProgressBar {
                    border: 2px solid #2c2c2c;
                    border-radius: 6px;
                    background-color: #1e1e1e;
                    padding: 2px;
                    text-align: center;
                    color: #ffffff;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #ffffff;
                    border-radius: 4px;
                }
            """
        else:
            # Light mode: light backgrounds, dark text
            return """
                QMainWindow {
                    background-color: #ffffff;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    selection-background-color: #000000;
                    selection-color: #ffffff;
                }
                QLineEdit::placeholder {
                    color: #9e9e9e;
                }
                QLineEdit:focus {
                    border: 2px solid #000000;
                    outline: none;
                }
                QPushButton {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #eeeeee;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
                QPushButton:disabled {
                    background-color: #f0f0f0;
                    color: #9e9e9e;
                }
                QLabel {
                    color: #000000;
                    font-size: 12px;
                }
                QProgressBar {
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                    padding: 2px;
                    text-align: center;
                    color: #000000;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #000000;
                    border-radius: 4px;
                }
            """
