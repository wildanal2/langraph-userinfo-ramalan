# Widget Chatbot Documentation

## 📦 Struktur Widget

```
src/
├── static/
│   └── widget/
│       ├── css/
│       │   └── widget.css          # Styling widget
│       ├── js/
│       │   └── widget.js           # Logic widget
│       └── images/
│           └── krea-ai.png         # Logo
└── api/
    └── routes/
        └── widget.py               # Widget routes
```

## 🚀 Cara Penggunaan

### 1. Embed di Website Eksternal

Tambahkan kode berikut sebelum closing tag `</body>`:

```html
<!-- Krea.ai Chat Widget -->
<script>
  window.KREA_API_URL = 'http://localhost:8000';
</script>
<link rel="stylesheet" href="http://localhost:8000/static/widget/css/widget.css">
<script src="http://localhost:8000/static/widget/js/widget.js"></script>
```

### 2. Konfigurasi API URL

Untuk production, ubah API URL:

```html
<script>
  window.KREA_API_URL = 'https://api.yourdomain.com';
</script>
```

### 3. Kustomisasi Logo (Opsional)

Edit di `widget.js`:

```javascript
window.kreaWidget = new KreaChatWidget({
    apiUrl: 'https://api.yourdomain.com',
    logoUrl: 'https://yourdomain.com/custom-logo.png'
});
```

## 🎨 Endpoints Widget

### Demo Page
```
GET /widget/demo
```
Halaman demo lengkap dengan widget terintegrasi.

### Embed Code
```
GET /widget/embed
```
Halaman untuk mendapatkan embed code dan dokumentasi.

## 🔧 Fitur Widget

- ✅ Auto-initialize saat page load
- ✅ Session management dengan localStorage
- ✅ SSE streaming responses
- ✅ Interactive buttons (quick reply, fortune trigger, SSO)
- ✅ Responsive design
- ✅ Typing indicator
- ✅ Reset chat functionality
- ✅ Bold text parsing (**text**)
- ✅ Error handling

## 🎯 Kustomisasi CSS

Edit `src/static/widget/css/widget.css` untuk mengubah:

- Warna brand (default: purple-indigo gradient)
- Ukuran widget
- Posisi bubble
- Font dan spacing
- Animasi

Contoh ubah warna:

```css
.krea-chat-bubble {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}
```

## 📱 Responsive Behavior

Widget otomatis menyesuaikan dengan layar:
- Desktop: 384px width
- Mobile: Full width dengan margin 24px

## 🔐 Security

Widget menggunakan:
- CORS headers dari FastAPI
- Input sanitization
- Session validation
- Error boundaries

## 🧪 Testing

### Local Testing
```bash
# 1. Start FastAPI server
make run-dev

# 2. Buka browser
http://localhost:8000/widget/demo
```

### Embed Testing
Buat file HTML test:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Widget Test</title>
</head>
<body>
    <h1>Test Page</h1>
    
    <script>
      window.KREA_API_URL = 'http://localhost:8000';
    </script>
    <link rel="stylesheet" href="http://localhost:8000/static/widget/css/widget.css">
    <script src="http://localhost:8000/static/widget/js/widget.js"></script>
</body>
</html>
```

## 🚀 Production Deployment

### 1. Update API URL
Ganti semua `localhost:8000` dengan domain production Anda.

### 2. CDN (Opsional)
Upload static files ke CDN untuk performa lebih baik:

```html
<link rel="stylesheet" href="https://cdn.yourdomain.com/widget/css/widget.css">
<script src="https://cdn.yourdomain.com/widget/js/widget.js"></script>
```

### 3. Minify Assets
```bash
# CSS
npx cssnano src/static/widget/css/widget.css src/static/widget/css/widget.min.css

# JS
npx terser src/static/widget/js/widget.js -o src/static/widget/js/widget.min.js
```

### 4. Cache Headers
FastAPI StaticFiles sudah include cache headers otomatis.

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Widget tidak muncul | Check console errors, pastikan CSS & JS loaded |
| CORS error | Update `allowed_origins` di `settings.py` |
| API connection failed | Verify `KREA_API_URL` benar |
| Session tidak persist | Check localStorage enabled di browser |
| Logo tidak muncul | Verify path `/static/widget/images/krea-ai.png` |

## 📊 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🔄 Update Widget

Untuk update widget di website yang sudah embed:

1. Update file di `src/static/widget/`
2. Restart FastAPI server
3. Clear browser cache atau tambahkan version query:

```html
<link rel="stylesheet" href="/static/widget/css/widget.css?v=1.1">
<script src="/static/widget/js/widget.js?v=1.1"></script>
```

## 📝 API Integration

Widget menggunakan endpoints berikut:

- `POST /start-message` - Initialize chat
- `POST /chat/stream` - Send message (SSE)
- `POST /reset` - Reset session

Lihat [README.md](../README.md) untuk detail API.

## 💡 Best Practices

1. **Performance**: Load widget script async jika tidak critical
2. **Privacy**: Inform users tentang data collection
3. **Accessibility**: Widget sudah include ARIA labels
4. **Mobile**: Test di berbagai device sizes
5. **Analytics**: Track widget interactions untuk insights

## 🎓 Advanced Usage

### Custom Event Listeners

```javascript
// Listen to widget events
window.addEventListener('load', () => {
    const widget = window.kreaWidget;
    
    // Custom logic after widget initialized
    console.log('Widget ready!');
});
```

### Programmatic Control

```javascript
// Open widget programmatically
window.kreaWidget.toggleWidget();

// Send message programmatically
window.kreaWidget.selectOption('Custom message');

// Reset chat
window.kreaWidget.resetChat();
```

## 📞 Support

Untuk pertanyaan atau issue, buka GitHub Issues atau contact tim development.
