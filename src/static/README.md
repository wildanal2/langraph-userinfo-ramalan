# Static Widget Files

Folder ini berisi aset untuk embeddable chat widget.

## Struktur

```
widget/
├── css/
│   └── widget.css      # Styling widget
├── js/
│   └── widget.js       # Widget logic & API integration
└── images/
    └── krea-ai.png     # Logo chatbot
```

## Akses Files

Files ini di-serve melalui FastAPI StaticFiles:

- CSS: `http://localhost:8000/static/widget/css/widget.css`
- JS: `http://localhost:8000/static/widget/js/widget.js`
- Logo: `http://localhost:8000/static/widget/images/krea-ai.png`

## Dokumentasi

Lihat [WIDGET.md](../../WIDGET.md) untuk dokumentasi lengkap.
