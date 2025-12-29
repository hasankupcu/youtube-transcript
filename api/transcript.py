from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import re

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, NoTranscriptAvailable
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

def extract_video_id(url):
    if not url:
        return None
    patterns = [r'[?&]v=([a-zA-Z0-9_-]{11})', r'youtu\.be/([a-zA-Z0-9_-]{11})', r'shorts/([a-zA-Z0-9_-]{11})', r'embed/([a-zA-Z0-9_-]{11})']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    return None

def get_transcript(video_id, lang='tr'):
    if not YOUTUBE_API_AVAILABLE:
        return {"success": False, "error": "youtube-transcript-api not installed"}
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [{"code": t.language_code, "label": t.language, "is_generated": t.is_generated} for t in transcript_list]
        transcript_data = None
        used_lang = None
        for transcript in transcript_list:
            if transcript.language_code == lang:
                transcript_data = transcript.fetch()
                used_lang = transcript.language_code
                break
        if not transcript_data:
            for transcript in transcript_list:
                transcript_data = transcript.fetch()
                used_lang = transcript.language_code
                break
        if not transcript_data:
            return {"success": False, "error": "Transkript bulunamadı", "video_id": video_id, "available_languages": available_languages}
        segments = []
        full_text = ""
        for item in transcript_data:
            text = item.get('text', '').strip()
            if text:
                segments.append({"start": round(item.get('start', 0), 2), "duration": round(item.get('duration', 0), 2), "text": text})
                full_text += text + " "
        total_duration = segments[-1]['start'] + segments[-1]['duration'] if segments else 0
        return {"success": True, "video_id": video_id, "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg", "language": used_lang, "available_languages": available_languages, "full_text": full_text.strip(), "segments": segments, "word_count": len(full_text.split()), "segment_count": len(segments), "duration_seconds": int(total_duration)}
    except TranscriptsDisabled:
        return {"success": False, "error": "Bu video için altyazılar devre dışı", "video_id": video_id}
    except NoTranscriptFound:
        return {"success": False, "error": "Transkript bulunamadı", "video_id": video_id}
    except VideoUnavailable:
        return {"success": False, "error": "Video mevcut değil", "video_id": video_id}
    except Exception as e:
        return {"success": False, "error": str(e), "video_id": video_id}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        video_url = params.get('url', params.get('v', ['']))[0]
        lang = params.get('lang', ['tr'])[0]
        if not video_url:
            result = {"success": False, "error": "URL parametresi gerekli"}
        else:
            video_id = extract_video_id(video_url)
            if not video_id:
                result = {"success": False, "error": "Geçersiz YouTube URL"}
            else:
                result = get_transcript(video_id, lang)
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()
