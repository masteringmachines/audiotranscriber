"""Entry point for `lingua-web` console script."""
import os
from .app import create_app

def main():
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Lingua running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
