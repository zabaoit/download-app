# 📥 Download Video App - Tải Video Đa Nền Tảng

Ứng dụng desktop GUI đơn giản, mạnh mẽ để tải video từ YouTube, TikTok, Instagram, Facebook và 1000+ nền tảng khác. **Tự động chuyển đổi HEVC → H.264 để tương thích 100% Windows Media Player.**

---

## ✨ Tính Năng Chính

✅ **Tải từ 1000+ nền tảng** - YouTube, TikTok, Instagram, Facebook, v.v.  
✅ **Tự động convert HEVC → H.264** - Phát hiện codec HEVC và transcode sang H.264 + AAC  
✅ **Chọn chất lượng** - Auto / 1080p / 720p / Audio-only  
✅ **Chọn thư mục lưu** - Giao diện folder selection  
✅ **Tiến trình real-time** - Progress bar + ETA  
✅ **Giao diện hiện đại** - Material Design, dễ sử dụng  
✅ **Build .exe** - Chạy độc lập, không cần Python  

---

## 🛠️ Yêu Cầu

### 1. Python 3.8+
```powershell
python --version
```
Tải từ: https://www.python.org/downloads/

### 2. FFmpeg 8.0+
```powershell
ffmpeg -version
```

**Windows (WinGet):**
```powershell
winget install FFmpeg
```

**Windows (Chocolatey):**
```powershell
choco install ffmpeg
```

---

## 🚀 Cài Đặt & Chạy

### Bước 1: Tạo Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate
```

### Bước 2: Cài Dependencies
```powershell
pip install -r requirements.txt
```

### Bước 3: Chạy App
```powershell
python run.py
```

---

## 📦 Build Windows Executable

Tạo file `.exe` độc lập (8.4 MB):

```powershell
python build.py
```

Kết quả: `dist/DownloadApp/DownloadApp.exe`

---

## 📁 Project Structure

```
download-app/
├── run.py                 # Entry point
├── build.py               # Build .exe
├── requirements.txt       # Dependencies
├── README.md              # Tài liệu này
└── app/
    ├── app.py             # QApplication setup
    ├── gui.py             # UI + Download Worker
    ├── logger.py          # Logging
    ├── settings.py        # Settings persistence
    ├── security.py        # Input validation
    ├── queue_manager.py   # Queue management
    ├── icon.ico           # App icon
    └── icon.png           # App icon (PNG)
```

---

## 💻 Cách Sử Dụng

1. **Paste URL video** vào ô input
2. **Chọn chất lượng** (Auto/1080p/720p/Audio)
3. **Chọn thư mục** lưu (tuỳ chọn)
4. **Nhấn Download** hoặc Enter
5. **Chờ hoàn tất** - App tự động:
   - Tải video
   - Phát hiện HEVC
   - Convert sang H.264 (nếu cần)
   - Thông báo hoàn tất

**Nếu video là HEVC:** Quá trình transcode mất 1-5 phút tùy độ phân giải.

---

## 🔧 Tech Stack

| Công Nghệ | Phiên Bản |
|-----------|----------|
| Python | 3.12.10 |
| PySide6 | 6.10.0 |
| yt-dlp | 2025.11.12 |
| FFmpeg | 8.0 |

---

## ✅ Nền Tảng Được Hỗ Trợ

- ✅ YouTube (video, Shorts, playlist)
- ✅ TikTok (video, user profiles)
- ✅ Instagram
- ✅ Facebook
- ✅ 1000+ nền tảng khác via yt-dlp

---

## 🐛 Troubleshooting

### "ffmpeg: command not found"
```powershell
winget install FFmpeg
# Restart PowerShell
ffmpeg -version
```

### "ModuleNotFoundError: No module named 'PySide6'"
```powershell
.venv\Scripts\Activate
pip install -r requirements.txt
```

### "You need a new codec to play this item" (Windows Media Player)
✅ **Giải pháp:** Tải lại video với app. App sẽ tự động convert HEVC → H.264

---

## 📊 Thời Gian Encoding (ước tính)

| Độ phân giải | Thời gian | CPU |
|-------------|----------|-----|
| 480p | 30-60 giây | i5/Ryzen 5 |
| 720p | 1-2 phút | i5/Ryzen 5 |
| 1080p | 3-5 phút | i5/Ryzen 5 |

---

## 🎯 Format Selection

App sử dụng chiến lược đơn giản:
- **Priority 1:** `best` - Lấy format tốt nhất
- **Priority 2:** Fallback nếu format không khả dụng

Điều này đảm bảo hoạt động với 99% videos.

---

## 🎨 Tùy Chỉnh

### Đổi chất lượng encoding (app/gui.py)
```python
# Nhanh hơn (chất lượng kém)
"-preset", "ultrafast",

# Cân bằng (mặc định)
"-preset", "slow",

# Chất lượng cao (chậm)
"-preset", "slower",
```

### Đổi bitrate audio
```python
"-b:a", "256k",  # Current (256k)
"-b:a", "192k",  # Lower quality
"-b:a", "320k",  # Higher quality
```

---

## 📝 License

Dự án này cho mục đích cá nhân và học tập.

---

**Made with ❤️ using PySide6 + yt-dlp + FFmpeg**

*Last updated: November 27, 2025*
