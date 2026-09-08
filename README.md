<div align="center">

# 🌐 NanoGPS: Precision Tracker & Telemetry Profiler

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)
[![GitHub release](https://img.shields.io/badge/release-v1.3.0-orange.svg?style=for-the-badge)](https://github.com/trmxvibs/NanoGPS)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20WSL-lightgrey.svg?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/trmxvibs/NanoGPS)

<p align="center">
  <b>Advanced reconnaissance framework built for high-precision geolocation tracking and deep device telemetry fingerprinting.</b>
</p>

</div>

---

## 🚀 1. Overview & Core Features

**NanoGPS** is an advanced modular profiling framework engineered for security telemetry analysis, real-time activity monitoring, and comprehensive device fingerprinting. 

* 🎨 **Dynamic Brand Cloner:** Instantly generates customized branded verification portals (e.g., Instagram, Netflix, Google) on-the-fly with integrated username input capture.
* 📍 **Precision Geolocation:** Captures high-accuracy GPS coordinates along with accuracy radiuses and generates direct Google Maps redirection links.
* 🛡️ **Deep Device Telemetry:** Extracts hardware concurrency, device memory, storage quota estimates, client hints, screen orientation, touch points, battery stats, and WebGL GPU renderers.
* 🚇 **Multi-Tunnel & Localhost Support:** Flexible routing supporting Cloudflare (`cloudflared`), Serveo.net, Localhost.run, and mandatory Localhost direct modes for seamless local testing.
* 📊 **SQLite Database Integration:** Automatically logs all incoming hits, fingerprints, and coordinates securely into a local database (`auratrace.db`) with color-coded live terminal updates.

---

## 📁 2. Project Architecture

The project follows a clean, modular structure for easy maintenance and scalability:

```text
NanoGPS/
├── main.py         # Interactive CLI dashboard & control menu
├── server.py       # Threaded HTTP server, route mapper & IP intel
├── cloner.py       # Dynamic brand-cloned HTML template generator
├── tunnel.py       # Multi-tunnel coordinator (Cloudflare, SSH, Localhost)
├── database.py     # Secure SQLite database manager & logger
├── logger.py       # Local file audit logging & Telegram alert hooks
└── colors.py       # Terminal ANSI color schemes for live alerts
```


## ⚙️ 3. Installation & Quick Start
Get NanoGPS up and running on your local machine or server in just a few steps:

Prerequisites & Clone
Make sure Python 3.x is installed on your system.
```bash
# Clone the repository
git clone https://github.com/trmxvibs/NanoGPS.git
cd NanoGPS

# Install required dependencies
pip install requests
```
---
## Running the Tool
Launch the interactive CLI menu:
```python
python main.py
```
Select option [1] to start the dynamic trap server.

Enter your desired Template Brand Name (e.g., Instagram, Spotify).

Provide the final Target Redirect URL where the victim will be redirected post-capture.

Choose your preferred Tunneling Provider or use Localhost Direct for immediate browser testing.

Select option [2] anytime from the main menu to view all historical telemetry saved in the database.






































