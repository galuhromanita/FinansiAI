# Frontend Assets

Folder ini berisi semua asset frontend untuk aplikasi FinansiAI.

## Struktur

```
frontend/
├── templates/       # HTML templates (Jinja2)
│   ├── landing.html    # Landing page dengan CTA
│   ├── dashboard.html  # Dashboard upload file
│   ├── loading.html    # Loading animation
│   └── laporan.html    # Halaman laporan hasil analisis
└── static/          # Static assets
    ├── css/
    │   └── style.css   # Custom CSS
    └── image/
        └── *.jpg/jpeg  # Background images
```

## Teknologi

- **HTML5**: Struktur halaman
- **Tailwind CSS**: Framework CSS (via CDN)
- **Lucide Icons**: Icon library (via CDN)
- **Jinja2**: Template engine (dirender oleh backend FastAPI)

## Catatan

- Templates di-render oleh backend FastAPI menggunakan Jinja2Templates
- Static files di-serve melalui FastAPI StaticFiles middleware
- Semua path asset menggunakan helper `url_for()` untuk routing dinamis
