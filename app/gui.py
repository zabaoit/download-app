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
)
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor
import yt_dlp
from pathlib import Path
import subprocess
import os


class DownloadWorker(QObject):
    progress = Signal(int, str)  # percent, status text
    finished = Signal(bool, str)  # success, message/path

    def __init__(self, url: str, outdir: str):
        super().__init__()
        self.url = url
        self.outdir = outdir
        self._last_percent = 0
        self._last_filename = None

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
            outtmpl = str(Path(self.outdir) / "%(title)s.%(ext)s")
            ydl_opts = {
                "outtmpl": outtmpl,
                "progress_hooks": [self._progress_hook],
                "format": "best[ext=mp4]/best",
                "quiet": False,
                "no_warnings": False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            final_path = None
            if self._last_filename:
                src = Path(self._last_filename)
                # ensure absolute path
                if not src.is_absolute():
                    src = Path(self.outdir) / src.name

                if src.exists():
                    # attempt to remux/re-encode audio to AAC (widely supported)
                    # write to a temporary file in the same folder, then atomically replace
                    tmp = src.with_suffix('.tmp.mp4')
                    try:
                        self.progress.emit(0, "Tải sắp xong, vui lòng chờ...")
                        # encode video to h.264 and audio to aac
                        subprocess.run([
                            "ffmpeg",
                            "-y",
                            "-i",
                            str(src),
                            "-c:v",
                            "libx264",
                            "-preset",
                            "fast",
                            "-c:a",
                            "aac",
                            "-b:a",
                            "192k",
                            str(tmp),
                        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        # atomically replace original with tmp so only one file (original name) remains
                        try:
                            tmp.replace(src)
                            final_path = str(src)
                        except Exception:
                            try:
                                # fallback to os.replace
                                os.replace(str(tmp), str(src))
                                final_path = str(src)
                            except Exception:
                                # if replace fails, keep tmp as final
                                final_path = str(tmp)
                    except Exception:
                        # ffmpeg failed (or not installed) — fall back to original
                        final_path = str(src)
                else:
                    final_path = str(Path(self.outdir))
            else:
                final_path = str(Path(self.outdir))

            self.finished.emit(True, final_path)
        except Exception as e:
            self.finished.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📥 Download Video Đa Nền Tảng")
        self.setGeometry(100, 100, 700, 280)
        self.setStyleSheet(self._get_stylesheet())
        # Set window icon using emoji/text (fallback for Windows)
        self.setWindowIcon(self._create_icon())

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

        main_layout.addLayout(row1)

        # show selected folder
        self.folder_label = QLabel(f"📂 Lưu vào: {self.downloads_dir}")
        main_layout.addWidget(self.folder_label)

        # progress bar and status
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
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

    def choose_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu", str(self.downloads_dir))
        if path:
            self.downloads_dir = Path(path)
            self.folder_label.setText(f"Lưu vào: {self.downloads_dir}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.result_label.setText("Hãy nhập URL.")
            return

        # disable buttons while downloading
        self.download_btn.setEnabled(False)
        self.choose_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.result_label.setText("Bắt đầu tải...")

        # setup worker in a QThread
        self._thread = QThread()
        self._worker = DownloadWorker(url, str(self.downloads_dir))
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
        self._cleanup_after_cancel()

    def _on_progress(self, percent: int, text: str):
        self.progress_bar.setValue(percent)
        self.result_label.setText(text)

    def _on_finished(self, success: bool, message: str):
        if success:
            self.result_label.setText(f"Tải thành công! Lưu tại: {message}")
            self.progress_bar.setValue(100)
            self.url_input.clear()  # Clear input after successful download
        else:
            self.result_label.setText(f"Lỗi: {message}")

        # cleanup thread/worker
        if self._thread:
            self._thread.quit()
            self._thread.wait()
        self._cleanup_after_cancel()

    def _cleanup_after_cancel(self):
        self.download_btn.setEnabled(True)
        self.choose_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None
        self._thread = None

    def _get_stylesheet(self) -> str:
        """Return modern stylesheet for the application."""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLineEdit {
                background-color: white;
                color: #212121;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: #2196F3;
            }
            QLineEdit::placeholder {
                color: #bdbdbd;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                outline: none;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
            QLabel {
                color: #424242;
                font-size: 12px;
            }
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: #f0f0f0;
                padding: 2px;
                text-align: center;
                color: #2196F3;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 4px;
            }
        """
