from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import re

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        NoTranscriptAvailable
    )
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

def extract_video_id(url):
    """URL'den video ID çıkar"""
    if not url:
        return None
    
    patterns = [
        r'[?&]v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'shorts/([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None

def get_transcript(video_id, lang='tr'):
    """Transkript al"""
    if not YOUTUBE_API_AVAILABLE:
        return {
            "success": False,
            "error": "youtube-transcript-api kurulu değil"
        }
    
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        available_languages = []
        for transcript in transcript_list:
            available_languages.append({
                "code": transcript.language_code,
                "label": transcript.language,
                "is_generated": transcript.is_generated
            })
        
        transcript_data = None
        used_lang = None
        
        # İstenen dili bul
        for transcript in transcript_list:
            if transcript.language_code == lang:
                transcript_data = transcript.fetch()
                used_lang = transcript.language_code
                break
        
        # Bulunamadıysa ilk mevcut olanı al
        if not transcript_data:
            for transcript in transcript_list:
                transcript_data = transcript.fetch()
                used_lang = transcript.language_code
                break
        
        if not transcript_data:
            return {
                "success": False,
                "error": "Transkript bulunamadı",
                "video_id": video_id,
                "available_languages": available_languages
            }
        
        # Verileri işle
        segments = []
        full_text = ""
        
        for item in transcript_data:
            text = item.get('text', '').strip()
            if text:
                segments.append({
                    "start": round(item.get('start', 0), 2),
                    "duration": round(item.get('duration', 0), 2),
                    "text": text
                })
                full_text += text + " "
        
        # Süre hesapla
        total_duration = 0
        if segments:
            last_seg = segments[-1]
            total_duration = last_seg['start'] + last_seg['duration']
        
        return {
            "success": True,
            "video_id": video_id,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
            "language": used_lang,
            "available_languages": available_languages,
            "full_text": full_text.strip(),
            "segments": segments,
            "word_count": len(full_text.split()),
            "segment_count": len(segments),
            "duration_seconds": int(total_duration)
        }
        
    except TranscriptsDisabled:
        return {
            "success": False,
            "error": "Bu video için altyazılar devre dışı",
            "video_id": video_id
        }
    except NoTranscriptFound:
        return {
            "success": False,
            "error": "Bu video için transkript bulunamadı",
            "video_id": video_id
        }
    except VideoUnavailable:
        return {
            "success": False,
            "error": "Video mevcut değil",
            "video_id": video_id
        }
    except NoTranscriptAvailable:
        return {
            "success": False,
            "error": "Bu video için altyazı mevcut değil",
            "video_id": video_id
        }
    except Exception as e:
        error_msg = str(e)
        if "bot" in error_msg.lower() or "sign in" in error_msg.lower():
            return {
                "success": False,
                "error": "YouTube bot koruması aktif",
                "video_id": video_id
            }
        return {
            "success": False,
            "error": error_msg,
            "video_id": video_id
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        video_url = params.get('url', params.get('v', ['']))[0]
        lang = params.get('lang', ['tr'])[0]
        
        if not video_url:
            result = {
                "success": False,
                "error": "URL parametresi gerekli. Örnek: ?url=https://youtube.com/watch?v=VIDEO_ID"
            }
        else:
            video_id = extract_video_id(video_url)
            if not video_id:
                result = {
                    "success": False,
                    "error": "Geçersiz YouTube URL"
                }
            else:
                result = get_transcript(video_id, lang)
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
