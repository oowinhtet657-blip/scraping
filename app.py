"""
Simple Flask Web App untuk Facebook Group Scraper
===================================================
Akses: http://localhost:5000
Scraping dengan Chrome real-time + STOP support
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import json
import threading
import signal
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

app = Flask(__name__)
CORS(app)

# Global state untuk manage scraping tasks
scraping_state: Dict[str, Any] = {
    "active": False,
    "task": None,
    "loop": None,
    "cancelled": False
}

# Default config
DEFAULT_CONFIG = {
    "chrome_user_data_dir": r"C:\Users\KuroX66\AppData\Local\Google\Chrome\User Data",
    "chrome_profile": "Default",
    "chrome_executable": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "debug_port": 9222,
    "groups": [],
    "scroll_pause": (4.0, 6.0),
    "headless": False,
    "output_dir": "output",
    "save_json": False,
    "save_excel": True,
}

@app.route("/")
def index():
    """Halaman utama."""
    return render_template("index.html")

@app.route("/api/scrape", methods=["POST"])
def scrape():
    """
    API untuk mulai scraping.
    JSON body:
    {
        "url": "https://www.facebook.com/groups/...",
        "max_posts": 100,
        "debug_port": 9222
    }
    """
    global scraping_state
    
    # Check if already scraping
    if scraping_state["active"]:
        return jsonify({"error": "Scraping sudah berjalan. Gunakan /api/stop untuk menghentikan."}), 400
    
    try:
        # Lazy import
        from scraper import FBGroupScraper
        
        data = request.get_json()
        url = data.get("url", "").strip()
        max_posts = int(data.get("max_posts", 100))
        debug_port = int(data.get("debug_port", 9222))

        # Validasi
        if not url:
            return jsonify({"error": "URL tidak boleh kosong"}), 400
        
        # Validasi format URL Facebook Group
        if "facebook.com/groups/" not in url or ("#" in url and url.endswith("#")):
            return jsonify({
                "error": "URL tidak valid! Format yang benar: https://www.facebook.com/groups/[GROUP_ID]"
            }), 400
        
        if max_posts < 1 or max_posts > 500:
            return jsonify({"error": "Max posts harus 1-500"}), 400

        # Setup config
        config = DEFAULT_CONFIG.copy()
        config["debug_port"] = debug_port
        config["groups"] = [
            {
                "name": "scrape_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
                "url": url,
                "max_posts": max_posts
            }
        ]

        print(f"\n{'='*60}")
        print(f"[Web] Mulai scraping URL: {url}")
        print(f"[Web] Max posts: {max_posts}")
        print(f"[Web] Debug port: {debug_port}")
        print(f"{'='*60}\n")

        # Reset state
        scraping_state["cancelled"] = False
        scraping_state["active"] = True
        
        # Jalankan scraper di thread terpisah
        def run_scraper():
            try:
                scraper = FBGroupScraper(config, scraping_state)
                posts = asyncio.run(scraper.run())
                
                if scraping_state["cancelled"]:
                    print("[Web] ⚠️  Scraping dibatalkan oleh user")
                    return None
                
                return posts
            except Exception as e:
                print(f"[Web] ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                raise

        scraper_thread = threading.Thread(target=run_scraper, daemon=False)
        scraper_thread.start()
        scraper_thread.join()  # Tunggu selesai
        
        if scraping_state["cancelled"]:
            scraping_state["active"] = False
            return jsonify({
                "error": "Scraping dibatalkan oleh user",
                "cancelled": True
            }), 200

        # Get results
        scraper = FBGroupScraper(config, scraping_state)
        posts = asyncio.run(scraper.run())
        
        scraping_state["active"] = False

        return jsonify({
            "status": "success",
            "total_posts": len(posts),
            "posts": posts
        }), 200

    except Exception as e:
        scraping_state["active"] = False
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/stop", methods=["POST"])
def stop_scraping():
    """
    Stop scraping yang sedang berjalan.
    """
    global scraping_state
    
    if not scraping_state["active"]:
        return jsonify({"error": "Tidak ada scraping yang sedang berjalan"}), 400
    
    print("\n[Web] 🛑 STOP signal diterima. Menghentikan scraping...")
    scraping_state["cancelled"] = True
    
    # Tunggu sebentar untuk process cleanup
    import time
    time.sleep(1)
    
    if scraping_state["active"]:
        print("[Web] ⚠️  Force killing Chrome process...")
        os.system("taskkill /F /IM chrome.exe 2>nul")
    
    scraping_state["active"] = False
    
    return jsonify({
        "status": "stopped",
        "message": "Scraping dihentikan"
    }), 200

@app.route("/api/download/<format>", methods=["POST"])
def download(format):
    """
    Download hasil scraping dalam format JSON atau Excel.
    JSON body: { "posts": [...], "filename": "nama_file" }
    """
    try:
        # Lazy import
        from scraper import ExcelExporter
        
        data = request.get_json()
        posts = data.get("posts", [])
        filename = data.get("filename", "scrape_results").strip()

        if not posts:
            return jsonify({"error": "No posts to download"}), 400

        # Sanitize filename (hapus karakter yang tidak aman)
        import re as regex
        filename = regex.sub(r'[^a-zA-Z0-9_-]', '', filename)
        if not filename:
            filename = "scrape_results"

        if format == "json":
            filepath = f"output/{filename}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            return send_file(filepath, as_attachment=True, download_name=f"{filename}.json")

        elif format == "excel":
            filepath = f"output/{filename}.xlsx"
            ExcelExporter.export(posts, filepath)
            return send_file(filepath, as_attachment=True, download_name=f"{filename}.xlsx")

        else:
            return jsonify({"error": "Format tidak valid"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health():
    """Health check."""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    Path("output").mkdir(exist_ok=True)
    print("\n" + "="*60)
    print("🚀 Facebook Group Scraper Web App")
    print("="*60)
    print("Akses: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
