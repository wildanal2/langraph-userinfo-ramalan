# Widget Chatbot - Struktur Project

## 📁 Struktur Lengkap

```
LangchainCollectorUserInformation/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── health.py
│   │   │   └── widget.py          # ✨ NEW: Widget routes
│   │   └── main.py                # ✨ UPDATED: Static files mounting
│   └── static/                    # ✨ NEW: Static files folder
│       ├── __init__.py
│       ├── README.md
│       └── widget/
│           ├── css/
│           │   └── widget.css     # Widget styling
│           ├── js/
│           │   └── widget.js      # Widget logic
│           └── images/
│               └── krea-ai.png    # Logo
├── examples/
│   └── widget-test.html           # ✨ NEW: Standalone test page
├── WIDGET.md                      # ✨ NEW: Widget documentation
└── README.md                      # ✨ UPDATED: Widget info

```

## 🎯 Files yang Dibuat/Diupdate

### Baru Dibuat:
1. **src/static/widget/css/widget.css** - Styling profesional untuk widget
2. **src/static/widget/js/widget.js** - JavaScript modular dengan class-based
3. **src/api/routes/widget.py** - Routes untuk demo & embed code
4. **WIDGET.md** - Dokumentasi lengkap widget
5. **examples/widget-test.html** - Test page standalone
6. **src/static/README.md** - Dokumentasi folder static

### Diupdate:
1. **src/api/main.py** - Tambah StaticFiles mounting & widget router
2. **README.md** - Tambah informasi widget

## 🚀 Cara Menggunakan

### 1. Start Server
```bash
cd /Users/miew/Documents/PycharmProjects/LangchainCollectorUserInformation
make run-dev
```

### 2. Test Widget

**Option A: Demo Page Built-in**
```
http://localhost:8000/widget/demo
```

**Option B: Embed Code Page**
```
http://localhost:8000/widget/embed
```

**Option C: Standalone Test**
```
open examples/widget-test.html
```

### 3. Embed di Website Eksternal

Tambahkan sebelum `</body>`:
```html
<script>
  window.KREA_API_URL = 'http://localhost:8000';
</script>
<link rel="stylesheet" href="http://localhost:8000/static/widget/css/widget.css">
<script src="http://localhost:8000/static/widget/js/widget.js"></script>
```

## ✨ Fitur Widget

- ✅ Auto-initialize on page load
- ✅ Session management (localStorage)
- ✅ SSE streaming responses
- ✅ Interactive buttons (quick reply, fortune, SSO)
- ✅ Responsive design
- ✅ Typing indicator
- ✅ Reset functionality
- ✅ Bold text parsing
- ✅ Error handling
- ✅ Professional styling dengan gradient purple-indigo

## 🎨 Kustomisasi

### Ubah Warna Brand
Edit `src/static/widget/css/widget.css`:
```css
.krea-chat-bubble {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}
```

### Ubah Logo
Replace `src/static/widget/images/krea-ai.png` dengan logo Anda.

### Ubah API URL
```javascript
window.KREA_API_URL = 'https://your-api-domain.com';
```

## 📊 Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/widget/demo` | GET | Demo page dengan widget |
| `/widget/embed` | GET | Embed code & dokumentasi |
| `/static/widget/css/widget.css` | GET | Widget CSS |
| `/static/widget/js/widget.js` | GET | Widget JavaScript |
| `/static/widget/images/krea-ai.png` | GET | Logo |

## 🔧 Troubleshooting

**Widget tidak muncul:**
- Check browser console untuk errors
- Pastikan FastAPI server running
- Verify static files path correct

**CORS error:**
- Update `allowed_origins` di `src/core/config.py`
- Untuk development, sudah allow all origins

**Logo tidak muncul:**
- Verify file exists: `src/static/widget/images/krea-ai.png`
- Check path di browser: `http://localhost:8000/static/widget/images/krea-ai.png`

## 📝 Next Steps

1. Test widget di berbagai browser
2. Test responsive di mobile
3. Customize styling sesuai brand
4. Deploy ke production
5. Update API URL untuk production

## 🎓 Dokumentasi Lengkap

Lihat **WIDGET.md** untuk dokumentasi detail, advanced usage, dan best practices.
