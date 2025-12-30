"""Widget routes for serving chatbot widget."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["widget"])


@router.get("/widget/demo", response_class=HTMLResponse)
async def widget_demo():
    """Demo page untuk widget chatbot."""
    return """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ekonomi Kreatif Indonesia - Krea.ai</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <header class="bg-white shadow-sm">
        <div class="max-w-6xl mx-auto px-4 py-4">
            <h1 class="text-2xl font-bold text-gray-800">🎨 Ekonomi Kreatif Indonesia</h1>
        </div>
    </header>

    <section class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-20">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <h2 class="text-4xl font-bold mb-4">Wujudkan Potensi Kreatifmu</h2>
            <p class="text-xl text-purple-100">Bergabunglah dengan komunitas kreator Indonesia</p>
        </div>
    </section>

    <section class="max-w-6xl mx-auto px-4 py-16">
        <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-4xl mb-4">🎬</div>
                <h3 class="text-xl font-bold mb-2">Film & Video</h3>
                <p class="text-gray-600">Ciptakan karya visual yang menginspirasi</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-4xl mb-4">🎵</div>
                <h3 class="text-xl font-bold mb-2">Musik</h3>
                <p class="text-gray-600">Ekspresikan kreativitas melalui suara</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-4xl mb-4">🎨</div>
                <h3 class="text-xl font-bold mb-2">Seni & Desain</h3>
                <p class="text-gray-600">Wujudkan imajinasi dalam karya nyata</p>
            </div>
        </div>
    </section>

    <script>
        window.KREA_API_URL = 'http://localhost:8000';
    </script>
    <link rel="stylesheet" href="/static/widget/css/widget.css">
    <script src="/static/widget/js/widget.js"></script>
</body>
</html>
    """


@router.get("/widget/embed", response_class=HTMLResponse)
async def widget_embed_code():
    """Halaman untuk mendapatkan embed code widget."""
    return """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embed Krea.ai Widget</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">🔮 Embed Krea.ai Widget</h1>
        
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-bold mb-4">Cara Penggunaan</h2>
            <p class="text-gray-600 mb-4">Copy dan paste kode berikut ke dalam website Anda, sebelum closing tag <code class="bg-gray-100 px-2 py-1 rounded">&lt;/body&gt;</code>:</p>
            
            <div class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <pre><code>&lt;!-- Krea.ai Chat Widget --&gt;
&lt;script&gt;
  window.KREA_API_URL = 'http://localhost:8000';
&lt;/script&gt;
&lt;link rel="stylesheet" href="http://localhost:8000/static/widget/css/widget.css"&gt;
&lt;script src="http://localhost:8000/static/widget/js/widget.js"&gt;&lt;/script&gt;</code></pre>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-bold mb-4">Konfigurasi (Opsional)</h2>
            <p class="text-gray-600 mb-4">Anda dapat mengkustomisasi API URL dengan mengubah nilai <code class="bg-gray-100 px-2 py-1 rounded">KREA_API_URL</code>:</p>
            
            <div class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <pre><code>&lt;script&gt;
  window.KREA_API_URL = 'https://your-api-domain.com';
&lt;/script&gt;</code></pre>
            </div>
        </div>

        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
            <p class="text-blue-700">
                <strong>💡 Tips:</strong> Untuk production, ganti <code>localhost:8000</code> dengan domain API Anda yang sebenarnya.
            </p>
        </div>

        <div class="flex gap-4">
            <a href="/widget/demo" class="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700">
                Lihat Demo
            </a>
            <a href="/docs" class="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700">
                API Documentation
            </a>
        </div>
    </div>
</body>
</html>
    """
