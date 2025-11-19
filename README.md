# 📥 Download App - Tải Video Đa Nền Tảng

Một ứng dụng desktop GUI hiện đại và dễ sử dụng để tải video từ YouTube, Instagram, TikTok và nhiều nền tảng khác. Ứng dụng tự động encode video sang H.264 + AAC để tương thích 100% với Windows Media Player và các player khác.

---

## ✨ Tính Năng

- ⬇️ **Tải từ nhiều nền tảng** - YouTube, Instagram, TikTok, Facebook, v.v. (1000+ nền tảng thông qua yt-dlp)
- 🗁 **Chọn thư mục lưu** - Giao diện cho phép chọn thư mục lưu video trực tiếp
- 📊 **Hiển thị tiến trình** - Progress bar real-time + ETA khi tải video
- 🎬 **Tự động transcode HEVC → H.264** - Phát hiện codec HEVC (H.265) và tự động convert sang H.264 + AAC (tương thích 100% Windows Media Player)
- ⌨️ **Nhấn Enter để tải** - Paste URL → Nhấn Enter hoặc nút Download
- 🎨 **Giao diện hiện đại** - Material Design với Dark/Light mode, icon emoji, responsive layout
- 📝 **Xóa input tự động** - Ô URL tự xóa sau khi tải xong thành công
- 💾 **Chỉ giữ 1 file** - App tự động thay thế file gốc bằng file đã encode (không có file dư)
- 🎯 **Chọn chất lượng video** - Dropdown để chọn Auto/1080p/720p/Audio-only
- 🌙 **Dark/Light Mode** - Toggle theme để phù hợp với sở thích của bạn

---

## 🛠️ Tech Stack

### Frontend & UI
- **PySide6** (v6.x) - Qt6 Python bindings để xây dựng giao diện desktop cross-platform
- **Material Design** - Styling với QSS (Qt Stylesheet), màu xanh (#2196F3), rounded corners, responsive layout

### Backend & Processing
- **yt-dlp** - Video downloader hiện đại (fork của youtube-dl) hỗ trợ 1000+ nền tảng
- **FFmpeg** (v8.0+) - Video encoder, encode H.264 + AAC audio

### Threading & Async
- **QThread** - Non-blocking downloads, prevent UI freeze
- **Signal/Slot** - Qt event system để giao tiếp giữa worker thread và main thread

---

## 📋 Prerequisites

Trước khi bắt đầu, đảm bảo bạn đã cài đặt các yêu cầu sau:

### 1. Python 3.8 trở lên
- **Tải**: https://www.python.org/downloads/
- **Kiểm tra**: 
  ```powershell
  python --version
  # Hoặc
  python3 --version
  ```
- **Lưu ý**: Khi cài Python, chọn "Add Python to PATH"

### 2. FFmpeg 8.0 trở lên
- **Tải**: https://ffmpeg.org/download.html

**Hoặc cài qua package manager:**

| Hệ Điều Hành | Lệnh |
|---|---|
| **Windows (Chocolatey)** | `choco install ffmpeg` |
| **Windows (WinGet)** | `winget install FFmpeg` |
| **macOS (Homebrew)** | `brew install ffmpeg` |
| **Linux (Ubuntu/Debian)** | `sudo apt update && sudo apt install ffmpeg` |
| **Linux (Fedora/RHEL)** | `sudo dnf install ffmpeg` |

**Kiểm tra FFmpeg đã cài:**
```powershell
ffmpeg -version
```

### 3. Git (tuỳ chọn)
- Chỉ cần nếu clone repository
- **Tải**: https://git-scm.com/

---

## 🚀 Quick Start

### Bước 1: Clone / Download Dự Án

```powershell
# Nếu dùng git
git clone <repository-url>
cd download-app

# Hoặc download ZIP và giải nén
# cd /path/to/download-app
```

### Bước 2: Tạo Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài Đặt Python Dependencies

```bash
pip install -r requirements.txt
```

**Hoặc cài tay nếu không có requirements.txt:**
```bash
pip install PySide6 yt_dlp
```

### Bước 4: Đảm Bảo FFmpeg Hoạt Động

```powershell
ffmpeg -version
```

Nếu lỗi "ffmpeg not found", xem phần **Troubleshooting**.

### Bước 5: Chạy Ứng Dụng

**Từ thư mục dự án (root):**
```powershell
python run.py
```

**Hoặc:**
```powershell
python -m app.app
```

**Kết quả:** Cửa sổ GUI hiện lên. Thư mục mặc định để lưu video là `downloads/` trong thư mục dự án.

---

## 📁 Project Structure

```
download-app/
│
├── run.py                    # 🚀 Entry point - chạy: python run.py
├── app/
│   ├── __init__.py           # Package initializer
│   ├── app.py                # Main app logic + QApplication setup
│   └── gui.py                # GUI components + Worker thread + Stylesheet
├── downloads/                # 📂 Thư mục mặc định để lưu video
├── requirements.txt          # Python dependencies
├── README.md                 # File này
└── .gitignore               # (tuỳ chọn) Exclude venv/, downloads/
```

### Chi tiết từng file:

| File | Mục Đích |
|------|---------|
| `run.py` | Root-level entry point. Gọi `app.app.main()` |
| `app/__init__.py` | Biến folder `app` thành Python package |
| `app/app.py` | Khởi tạo `QApplication`, hiển thị `MainWindow`, chạy event loop |
| `app/gui.py` | Toàn bộ UI: `MainWindow`, `DownloadWorker`, styling |
| `downloads/` | Folder lưu video đã tải (tự tạo nếu chưa có) |

---

## 💻 Cách Sử Dụng

### Workflow Cơ Bản

1. **Dán URL video**
   - Paste URL từ YouTube, Instagram, TikTok, v.v. vào ô input
   
2. **Chọn thư mục** (tuỳ chọn)
   - Nhấn "🗁 Chọn thư mục" để chọn nơi lưu video
   - Mặc định sẽ lưu vào `downloads/`
   
3. **Bắt đầu tải**
   - Nhấn "⬇️ Download" hoặc nhấn **Enter** trong ô URL
   
4. **Theo dõi tiến trình**
   - Progress bar hiển thị % tải + ETA
   
5. **Chờ encode**
   - App tự động encode video sang H.264 + AAC (im lặng trong background)
   - Encoding có thể mất vài phút tùy độ phân giải
   
6. **Hoàn tất**
   - UI thông báo "Tải thành công! Lưu tại: [path]"
   - Ô URL tự xóa sạch

### Keyboard Shortcuts

| Phím | Hành động |
|------|----------|
| **Enter** (trong URL field) | Bắt đầu download |
| **Esc** | Hủy download (nút ✕) |

---

## 🎯 Features Chi Tiết

### 1. Auto-create Downloads Folder
```
Thư mục downloads/ sẽ tự động được tạo nếu chưa tồn tại.
Nó sẽ được tạo cùng cấp với file run.py
```

### 2. Auto-encode H.264 + AAC (với HEVC Detection)
**Vấn đề:**
- YouTube/Instagram/TikTok phục vụ HEVC (H.265) hoặc HLS format
- Windows Media Player không hỗ trợ HEVC (yêu cầu codec mắc tiền từ Microsoft Store)
- Một số video có thể là H.264 sẵn

**Giải pháp - Tính Năng HEVC Auto-Detect & Transcode:**
- App **tự động phát hiện** codec của video (dùng ffmpeg)
- Nếu video là **HEVC**: Tự động transcode sang H.264 (libx264) + AAC audio
- Nếu video là **H.264/VP9/AV1** (không phải HEVC): Giữ nguyên gốc (không encode lại)
- Người dùng **không cần làm gì**, quá trình diễn ra im lặng

**Progress Indicator:**
- Khi tải video: "Đang tải... 45%"
- Khi đang transcode (nếu cần): "Chuyển đổi video sang định dạng H.264..."
- Lúc xong: "Tải thành công! Lưu tại: [path]"

**Kết quả:**
- ✅ 100% tương thích với Windows Media Player
- ✅ Chất lượng cao (CRF 20, preset medium)
- ✅ Người dùng có thể mở file ngay, không cần cài codec riêng

**Thời gian transcode:**
- 720p HEVC video: ~30-60 giây
- 1080p HEVC video: ~2-4 phút
- Video non-HEVC: 0 giây (không cần transcode)

### 3. Real-time Progress Tracking
- Hiển thị % tải + ETA trong quá trình download
- Ô progress bar được cập nhật liên tục (mỗi 1% change)
- Sau khi encode xong, progress = 100%

### 4. Single Output File (Atomic Replacement)
- Download sang temporary file `.tmp.mp4`
- Encode sang file temp mới
- Ngay khi encode xong, thay thế file gốc (atomically)
- **Kết quả:** Chỉ có 1 file `.mp4` final (không có file dư)

### 5. Auto-clear Input
- Ô URL tự xóa sau khi download thành công
- Sẵn sàng paste URL mới ngay lập tức

### 6. Modern UI
- Material Design với màu xanh (#2196F3)
- Emoji icons: 📥 (app), 🗁 (folder), ⬇️ (download), ✕ (cancel)
- Responsive layout với QVBoxLayout/QHBoxLayout
- Shadow effect, rounded corners, smooth styling

---

## 🐛 Troubleshooting

### Lỗi 1: "ffmpeg: command not found" hoặc "ffmpeg is not recognized"

**Nguyên nhân:** FFmpeg chưa được cài hoặc chưa trong Windows PATH

**Giải pháp:**

**Bước 1:** Cài FFmpeg
```powershell
# Nếu dùng WinGet (khuyến nghị)
winget install FFmpeg

# Hoặc nếu dùng Chocolatey
choco install ffmpeg
```

**Bước 2:** Restart PowerShell để cập nhật PATH
```powershell
exit
# Mở PowerShell mới
```

**Bước 3:** Kiểm tra
```powershell
ffmpeg -version
```

**Nếu vẫn lỗi, cài tay:**
1. Download từ https://ffmpeg.org/download.html
2. Giải nén vào `C:\Program Files\ffmpeg`
3. Thêm `C:\Program Files\ffmpeg\bin` vào Windows PATH:
   - Bấm `Win + X` → "System"
   - Bấm "Advanced system settings"
   - Bấm "Environment Variables"
   - Chọn "Path" (hoặc "PATH") → Edit
   - Bấm "New" → Nhập `C:\Program Files\ffmpeg\bin`
   - Bấm "OK" tất cả
4. Restart PowerShell

---

### Lỗi 2: "ModuleNotFoundError: No module named 'PySide6'"

**Nguyên nhân:** PySide6 chưa được cài hoặc virtual environment chưa được kích hoạt

**Giải pháp:**

**Bước 1:** Đảm bảo virtual environment được kích hoạt
```powershell
# Windows
venv\Scripts\Activate

# macOS / Linux
source venv/bin/activate
```

**Bước 2:** Cài lại packages
```bash
pip install -r requirements.txt
# Hoặc
pip install PySide6 yt_dlp
```

**Bước 3:** Chạy lại ứng dụng
```powershell
python run.py
```

---

### Lỗi 3: "ModuleNotFoundError: No module named 'app'"

**Nguyên nhân:** Chạy `python app/app.py` từ thư mục root (không đúng cách)

**Giải pháp:** Luôn chạy từ thư mục dự án (root):
```powershell
python run.py
# KHÔNG chạy: python app/app.py
```

---

### Lỗi 4: "You need a new codec to play this item" (Windows Media Player)

**Nguyên nhân:** Video sử dụng codec HEVC (H.265) mà Windows Media Player mặc định không hỗ trợ

**Giải pháp:**

**Option 1: Tải lại với ứng dụng (KHUYẾN NGHỊ)**
1. Đảm bảo FFmpeg đã được cài (xem Lỗi 1)
2. Restart PowerShell để cập nhật PATH
3. Chạy lại app: `python run.py`
4. Tải lại video - app sẽ **tự động phát hiện HEVC** và **transcode sang H.264** (không cần làm gì)
5. Video mới sẽ mở được trên Windows Media Player 100%

**Option 2: Tải codec từ Microsoft Store (không khuyến khích)**
- Video sẽ yêu cầu: "HEVC Video Extensions" ($0.99)
- Cài từ: https://www.microsoft.com/en-us/p/hevc-video-extensions/9nmzlz57r3t7

**Option 3: Dùng player khác (VLC, MPV)**
- VLC Player: https://www.videolan.org/
- MPV Player: https://mpv.io/
- Cả hai đều hỗ trợ HEVC sẵn

**Cách kiểm tra codec của video:**
```powershell
ffmpeg -i "C:\path\to\video.mp4" 2>&1 | findstr "Video:"
# Nếu thấy "hevc" hoặc "h265" → video là HEVC
# Nếu thấy "h264" hoặc "avc1" → video là H.264 (tương thích WMP)
```

**Tóm tắt:**
- App mới nhất **tự động detect & transcode HEVC** → Không cần lo lắng 🎉
- Nếu cũ video trước đó (trước v1.0.3), hãy tải lại với bản mới

---

### Lỗi 5: "No Internet connection" hoặc "Connection timeout"

**Nguyên nhân:** Mất kết nối mạng hoặc URL không hợp lệ

**Giải pháp:**
1. Kiểm tra kết nối Internet (ping Google)
2. Xác nhận URL đúng & hợp lệ
3. Thử URL khác
4. Nếu còn lỗi, URL có thể:
   - Video bị xóa
   - Video bị khóa theo địa lý (geo-blocked)
   - Nền tảng chặn yt-dlp

---

### Lỗi 6: GUI không hiển thị hoặc ứng dụng crash ngay khi chạy

**Nguyên nhân:** Môi trường headless (không có giao diện) hoặc PySide6 không tương thích với display

**Giải pháp:**
1. Đảm bảo chạy trên máy có **giao diện đồ họa** (không ssh/remote)
2. Nếu chạy qua remote, kích hoạt X11 forwarding (Linux)
3. Nếu chạy WSL (Windows Subsystem for Linux), xem phần "Development Tips"

---

### Lỗi 7: Encoding quá lâu hoặc app bị "hang"

**Nguyên nhân:** Preset "fast" vẫn có thể mất vài phút cho video lớn

**Giải pháp:**
1. **Đợi** - Encoding là bình thường. Video 1080p mất 3-5 phút
2. **Tăng tốc độ** - Sửa trong `app/gui.py`:
   ```python
   # Thay từ:
   "-preset", "fast",
   
   # Thành:
   "-preset", "ultrafast",  # Nhanh nhất nhưng chất lượng kém hơn
   ```

---

### Lỗi 8: "Permission denied" hoặc "Access is denied"

**Nguyên nhân:** App không có quyền ghi vào thư mục đã chọn

**Giải pháp:**
1. Chọn thư mục khác (với quyền ghi)
2. Chạy PowerShell **dưới quyền Admin**
3. Kiểm tra quyền folder: Chuột phải → Properties → Security → Edit

---

## 🔧 Development Tips

### Chạy Ứng Dụng Ở Chế Độ Debug

```bash
python run.py
# Console sẽ in log từ yt-dlp (nếu có)
```

### Xem Log FFmpeg Chi Tiết

Hiện tại app chặn output từ ffmpeg (`DEVNULL`). Để debug, sửa `app/gui.py`:

**Tìm dòng:**
```python
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```

**Thay thành:**
```python
])  # Sẽ in tất cả log ffmpeg ra console
```

### Thay Đổi Folder Mặc Định

Sửa trong `app/gui.py`, trong class `MainWindow.__init__()`:

**Tìm:**
```python
self.downloads_dir = Path(__file__).resolve().parents[1] / "downloads"
```

**Thay thành:**
```python
self.downloads_dir = Path("C:/Users/YourName/Videos")  # Custom folder
```

### Thay Đổi Quality / Format

Sửa trong `app/gui.py`, trong method `DownloadWorker.run()`:

**Tìm:**
```python
"format": "best[ext=mp4]/best",
```

**Thay thành:**
```python
# Chỉ lấy 1080p hoặc thấp hơn
"format": "bestvideo[height<=1080]+bestaudio/best",

# Hoặc chỉ tải video, không tải audio (nhanh hơn)
"format": "bestvideo[ext=mp4]/best",
```

### Chạy Syntax Check

```bash
python -m py_compile app/gui.py
python -m py_compile app/app.py
```

Nếu không có output = OK

### Testing

```bash
# Kiểm tra import
python -c "import PySide6; import yt_dlp; print('All imports OK')"

# Kiểm tra FFmpeg
ffmpeg -version
```

### Hot Reload (Development)

Hiện tại không hỗ trợ hot reload. Để thay đổi, cần restart app:
```bash
python run.py
```

---

## ⚙️ Configuration

### Sử Dụng Proxy

Sửa trong `app/gui.py`, method `DownloadWorker.run()`:

```python
ydl_opts = {
    "proxy": "http://[user:passwd@]proxy.server:port",
    "format": "best[ext=mp4]/best",
    ...
}
```

### Custom Output Filename

Sửa trong `app/gui.py`, method `DownloadWorker.run()`:

```python
# Hiện tại:
outtmpl = str(Path(self.outdir) / "%(title)s.%(ext)s")

# Custom examples:
# Với uploader name:
outtmpl = str(Path(self.outdir) / "[%(uploader)s] %(title)s.%(ext)s")

# Với ngày:
outtmpl = str(Path(self.outdir) / "%(upload_date)s - %(title)s.%(ext)s")

# Với ID:
outtmpl = str(Path(self.outdir) / "%(id)s - %(title)s.%(ext)s")
```

### Custom Audio Bitrate

Sửa trong `app/gui.py`, method `DownloadWorker.run()`:

```python
# Hiện tại: AAC 192k
"-b:a", "192k",

# Options:
"-b:a", "128k",  # Thấp hơn, file nhỏ hơn
"-b:a", "256k",  # Cao hơn, chất lượng tốt hơn
```

---

## 📊 Performance

### Encoding Time Estimates

| Độ Phân Giải | Thời Gian | Máy (CPU) |
|---|---|---|
| 480p | ~30-60 giây | Intel i5/Ryzen 5 |
| 720p | ~1-2 phút | Intel i5/Ryzen 5 |
| 1080p | ~3-5 phút | Intel i5/Ryzen 5 |
| 4K | ~10-20 phút | Intel i7/Ryzen 7 |

### Optimize cho Tốc Độ

Sửa preset sang "ultrafast":
```python
"-preset", "ultrafast",  # Nhanh nhất (chất lượng kém)
# "-preset", "superfast",  # Nhanh (chất lượng trung bình)
# "-preset", "fast",       # Cân bằng (mặc định)
# "-preset", "medium",     # Chậm (chất lượng tốt)
```

---

## 📄 License

Dự án này được cung cấp "as-is" cho mục đích cá nhân và học tập. Xem file `LICENSE` (nếu có) để biết thêm chi tiết.

---

## 🤝 Support

Nếu gặp vấn đề:

1. **Đọc README này kỹ** - Đặc biệt phần Troubleshooting
2. **Kiểm tra Prerequisites** - Đảm bảo Python 3.8+ và FFmpeg 8.0+ đã cài
3. **Xem Console Output** - Chạy `python run.py` và xem lỗi cụ thể
4. **Thử lại** - Restart PowerShell, cài lại packages, reset venv
5. **Kiểm tra Dependencies:**
   ```bash
   pip list | findstr "PySide6 yt_dlp"
   ```

---

**Made with zabaoit using PySide6 + yt-dlp + FFmpeg**

*Last updated: 2025*
