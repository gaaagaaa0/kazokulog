from backend.app.main import app

# Vercel用のハンドラー
def handler(request):
    return app(request.environ, lambda status, headers: None)