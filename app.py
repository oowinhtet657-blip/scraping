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
        "debug_port": 9222,
        "export_name": "nama_file_export"
    }
    """
    global scraping_state
    
    # Check if already scraping
    if scraping_state["active"]:
        return jsonify({"error": "Scraping sudah berjalan. Gunakan /api/stop untuk menghentikan."}), 400
    
    try:
        # Lazy import
        from scraper import FBGroupScraper, ExcelExporter
        import re as regex
        
        data = request.get_json()
        url = data.get("url", "").strip()
        max_posts = int(data.get("max_posts", 100))
        debug_port = int(data.get("debug_port", 9222))
        export_name = data.get("export_name", "scrape_results").strip()
        
        # Sanitize filename
        export_name = regex.sub(r'[^a-zA-Z0-9_-]', '', export_name)
        if not export_name:
            export_name = "scrape_results"

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
        scraping_state["results"] = None
        scraping_state["error"] = None
        
        # Jalankan scraper di thread terpisah
        def run_scraper():
            try:
                print("[Web] 🧵 Starting scraper thread...")
                scraper = FBGroupScraper(config, scraping_state)
                posts = asyncio.run(scraper.run())
                
                if scraping_state["cancelled"]:
                    print("[Web] ⚠️  Scraping dibatalkan oleh user")
                    scraping_state["results"] = None
                    return
                
                print(f"[Web] ✅ Thread scraped {len(posts)} posts successfully")
                scraping_state["results"] = posts
                
            except Exception as e:
                error_msg = str(e)
                print(f"[Web] ❌ Thread error: {error_msg}")
                import traceback
                traceback.print_exc()
                scraping_state["error"] = error_msg

        scraper_thread = threading.Thread(target=run_scraper, daemon=False)
        scraper_thread.start()
        scraper_thread.join()  # Tunggu selesai
        
        # Check hasil dari thread
        if scraping_state["cancelled"]:
            scraping_state["active"] = False
            return jsonify({
                "error": "Scraping dibatalkan oleh user",
                "cancelled": True
            }), 200
        
        if scraping_state["error"]:
            scraping_state["active"] = False
            return jsonify({
                "error": scraping_state["error"]
            }), 500
        
        posts = scraping_state.get("results", [])
        scraping_state["active"] = False
        
        # Auto-save Excel file setelah scraping selesai
        if posts:
            try:
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                filepath = os.path.join(output_dir, f"{export_name}.xlsx")
                ExcelExporter.export(posts, filepath)
                print(f"[Web] ✅ File Excel otomatis disimpan: {filepath}")
            except Exception as e:
                print(f"[Web] ⚠️  Gagal auto-save Excel: {e}")
                # Jangan return error, tetap return results agar user bisa download manual

        return jsonify({
            "status": "success",
            "total_posts": len(posts),
            "posts": posts,
            "export_filename": export_name
        }), 200

    except Exception as e:
        scraping_state["active"] = False
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/stop", methods=["POST"])
def stop_scraping():
    """
    Stop scraping yang sedang berjalan tanpa kill Chrome.
    Hanya set flag cancellation, biarkan scraper graceful shutdown.
    """
    global scraping_state
    
    if not scraping_state["active"]:
        return jsonify({"error": "Tidak ada scraping yang sedang berjalan"}), 400
    
    print("\n[Web] 🛑 STOP signal diterima. Set cancelled flag...")
    scraping_state["cancelled"] = True
    print("[Web] ✅ Flag cancelled=True. Scraper akan berhenti di checkpoint berikutnya...")
    
    return jsonify({
        "status": "stopping",
        "message": "Scraping akan dihentikan (graceful shutdown)"
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
