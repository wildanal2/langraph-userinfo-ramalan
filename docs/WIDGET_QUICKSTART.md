# Widget Quick Start Guide 🚀

## Setup dalam 3 Menit

### 1. Start Server
```bash
make run-dev
```

### 2. Test Widget
Buka browser:
```
http://localhost:8000/widget/demo
```

### 3. Embed di Website Anda
Copy-paste sebelum `</body>`:
```html
<script>window.KREA_API_URL = 'http://localhost:8000';</script>
<link rel="stylesheet" href="http://localhost:8000/static/widget/css/widget.css">
<script src="http://localhost:8000/static/widget/js/widget.js"></script>
```

## Struktur Files

```
src/static/widget/
├── css/widget.css          # Styling
├── js/widget.js            # Logic
└── images/krea-ai.png      # Logo
```

## Endpoints

- `/widget/demo` - Demo page
- `/widget/embed` - Embed code
- `/static/widget/*` - Static files

## Kustomisasi

### Ubah Logo
Replace: `src/static/widget/images/krea-ai.png`

### Ubah Warna
Edit: `src/static/widget/css/widget.css`
```css
.krea-chat-bubble {
    background: linear-gradient(135deg, #YOUR_COLOR 0%, #YOUR_COLOR 100%);
}
```

### Production API
```html
<script>window.KREA_API_URL = 'https://api.yourdomain.com';</script>
```

## Dokumentasi Lengkap
- **WIDGET.md** - Full documentation
- **WIDGET_STRUCTURE.md** - Project structure

## Support
Check console untuk debugging atau lihat logs FastAPI.
