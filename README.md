# 🌐 NanoGPS — Precision Tracker & Telemetry Profiler

<p align="center">
  <img src="https://img.shields.io/badge/NanoGPS-v1.3.0-00c853?style=for-the-badge&logo=target&logoColor=white" alt="NanoGPS Version">
  <img src="https://img.shields.io/badge/Status-Stable-00c853?style=for-the-badge" alt="Stable">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-00c853?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License">
</p>

<p align="center">
  <strong>Modular security telemetry analysis, geolocation testing, and device fingerprinting framework.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-testing">Testing</a> •
  <a href="#-security">Security</a>
</p>

---

## ⚡ Overview

**NanoGPS** is a modular Python framework for **authorized security telemetry testing**, combining controlled geolocation collection, browser/device capability profiling, local event logging, and tunnel-assisted testing into a single CLI-driven workflow.

It is designed for researchers, developers, and security teams who need a practical environment for studying what information a browser can expose when a user **explicitly grants the relevant permissions**.

> **Important:** NanoGPS is intended for systems, devices, accounts, and test participants for which you have explicit authorization. It must not be used for covert tracking, credential harvesting, impersonation, or unauthorized collection of personal data.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📍 **Precision Geolocation Testing** | Collects browser-provided coordinates and accuracy information after permission is granted. |
| 🧬 **Device Telemetry Profiling** | Profiles browser-exposed capabilities such as CPU concurrency, memory hints, storage estimates, display characteristics, touch support, and WebGL information. |
| 🖥️ **Interactive CLI** | Simple terminal dashboard for starting tests and reviewing locally stored events. |
| 🗄️ **SQLite Logging** | Stores test telemetry locally in an SQLite database for analysis. |
| 🌐 **Localhost Testing** | Supports direct local testing without requiring a public tunnel. |
| 🚇 **Tunnel Integration** | Provides configurable tunnel support for authorized remote test environments. |
| 🎨 **Template System** | Supports configurable test/verification pages for controlled security research environments. |
| 📊 **Live Telemetry Output** | Displays incoming test events and collected telemetry in the terminal. |
| 🧾 **Audit Logging** | Maintains local operational logs for troubleshooting and test auditing. |
| 🧪 **CI Verification** | Includes GitHub Actions workflow support for automated project checks. |

---

## 🧠 What NanoGPS Demonstrates

Modern browsers can expose a surprisingly rich set of signals to web applications.

Depending on browser support, permissions, and privacy settings, a controlled test can reveal information such as:

- 🌍 Geolocation coordinates
- 🎯 Location accuracy
- 🖥️ Screen dimensions and orientation
- ⚙️ Hardware concurrency
- 🧠 Device-memory hints
- 💾 Storage quota estimates
- 👆 Touch-point capabilities
- 🔋 Battery information where supported
- 🎮 WebGL renderer information where exposed
- 🌐 Browser/client capability information
- 🌎 Network-facing IP information available to the server

NanoGPS provides a single environment for observing and analyzing these signals during **authorized testing**.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      NanoGPS CLI     │
                         │       main.py        │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
      │   Server    │       │   Cloner    │       │   Tunnel    │
      │  server.py  │       │ cloner.py   │       │ tunnel.py   │
      └──────┬──────┘       └─────────────┘       └──────┬──────┘
             │                                             │
             │ telemetry                                  │
             ▼                                             ▼
      ┌─────────────┐                              ┌─────────────┐
      │  Database   │                              │ Test Access │
      │database.py  │                              │ Local/Tunnel │
      └──────┬──────┘                              └─────────────┘
             │
             ▼
      ┌─────────────┐
      │ auratrace.db│
      └─────────────┘

             ┌─────────────┐
             │   Logger    │
             │ logger.py   │
             └─────────────┘
                    │
                    ▼
              Audit / Alerts
```

---

# 📁 Project Structure

```text
NanoGPS/
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI workflow
│
├── main.py                        # Interactive CLI dashboard
├── server.py                      # HTTP server and route handling
├── cloner.py                      # Controlled HTML test-template generator
├── tunnel.py                      # Tunnel coordination
├── database.py                    # SQLite database manager
├── logger.py                      # Local audit logging
├── colors.py                      # Terminal color utilities
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT License
└── README.md                      # Project documentation
```

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/trmxvibs/NanoGPS.git
cd NanoGPS
```

## 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 3. Start NanoGPS

```bash
python main.py
```

---

# 🧪 Usage

After launching:

```bash
python main.py
```

the interactive dashboard provides the available testing operations.

### Typical authorized workflow

```text
[1] Start telemetry test
[2] View stored test events
```

### Test configuration

Depending on the version/configuration, the test workflow may allow you to define:

1. A controlled test-page/template name
2. A post-test redirect destination
3. A local or tunnel-based access mode
4. Telemetry monitoring options

For legitimate testing, use a clearly identified test page and obtain informed consent before collecting location or device information.

---

# 📍 Geolocation Testing

NanoGPS can be used to study browser geolocation behavior.

A typical browser flow is:

```text
User opens authorized test page
             │
             ▼
Browser requests location permission
             │
       ┌─────┴─────┐
       │           │
     Allow       Deny
       │           │
       ▼           ▼
Coordinates     No GPS data
       │
       ▼
Accuracy + Telemetry
       │
       ▼
Local SQLite Storage
```

### Example data model

```text
Latitude
Longitude
Accuracy
Timestamp
User-Agent / Client Information
Device Capability Signals
```

**No location permission should be bypassed.**

---

# 🧬 Device Telemetry

NanoGPS can organize browser-exposed telemetry into categories such as:

### Hardware

```text
CPU concurrency
Device-memory hint
Touch capability
```

### Display

```text
Screen resolution
Available screen size
Orientation
Pixel ratio
```

### Storage

```text
Storage quota estimate
Available browser storage signals
```

### Rendering

```text
WebGL vendor
WebGL renderer
Graphics capability information
```

### Browser / Client

```text
User-Agent
Client capability hints
Language
Platform information
```

Availability varies significantly between browsers and privacy configurations.

---

# 🗄️ Local Database

Telemetry generated during authorized testing can be stored in:

```text
auratrace.db
```

SQLite provides a lightweight local database suitable for development and security research.

Example conceptual record:

```text
┌────────────┬──────────────┬──────────────┬─────────────┐
│ Timestamp  │ Test Session │ Location     │ Telemetry   │
├────────────┼──────────────┼──────────────┼─────────────┤
│ 15:42:11   │ TEST-001     │ Permissioned │ Collected   │
└────────────┴──────────────┴──────────────┴─────────────┘
```

---

# 🌐 Localhost Mode

Localhost mode is recommended for initial development and debugging.

Start the application:

```bash
python main.py
```

Then access the local test endpoint using the address displayed by the application.

This allows developers to validate:

- HTTP routing
- HTML templates
- Browser permission behavior
- Telemetry parsing
- SQLite storage
- Terminal logging

without exposing the service publicly.

---

# 🚇 Tunnel Testing

For authorized remote testing, NanoGPS can integrate with supported tunnel mechanisms configured by the project.

Typical architecture:

```text
Browser
   │
   ▼
Public Test URL
   │
   ▼
Tunnel
   │
   ▼
NanoGPS HTTP Server
   │
   ├── Telemetry
   ├── Test Event
   └── Database
```

Use only tunnels and infrastructure that you control or are explicitly authorized to use.

---

# 🔐 Security & Privacy

NanoGPS handles potentially sensitive telemetry.

Recommended safeguards:

- ✅ Obtain explicit consent before collecting geolocation.
- ✅ Use test accounts and test devices.
- ✅ Keep collected data local whenever possible.
- ✅ Do not collect passwords or authentication tokens.
- ✅ Do not impersonate real services to deceive users.
- ✅ Do not deploy tracking pages against unsuspecting individuals.
- ✅ Restrict database permissions.
- ✅ Remove test data after research is complete.
- ✅ Do not publish raw coordinates or identifiable telemetry.
- ✅ Review third-party tunnel and logging configurations before use.

### Data minimization

Only collect the telemetry necessary for the specific research question.

---

# 🛡️ Threat-Modeling Use Cases

NanoGPS can support research into:

### Browser Privacy

Study how much information a website can derive from browser APIs.

### Security Awareness

Demonstrate why users should carefully review browser permission prompts.

### Fingerprinting Research

Analyze the uniqueness and stability of browser/device signals.

### Application Testing

Validate whether an application unnecessarily requests sensitive browser capabilities.

### SOC / Blue-Team Training

Generate controlled telemetry events for detection and investigation exercises.

### Privacy Engineering

Evaluate the effectiveness of browser privacy controls and anti-fingerprinting mechanisms.

---

# 🧪 Testing Checklist

Before considering a deployment ready:

```text
[ ] Local server starts successfully
[ ] SQLite database initializes correctly
[ ] Test page renders correctly
[ ] Permission-denied paths are handled
[ ] Invalid telemetry is rejected safely
[ ] Database input is validated
[ ] Logs do not expose unnecessary sensitive data
[ ] Tunnel failure does not crash the server
[ ] HTTP errors are handled cleanly
[ ] Test data can be deleted
[ ] CI checks pass
```

---

# ⚙️ Development

Run the application locally:

```bash
python main.py
```

For development, keep the environment isolated:

```bash
python -m venv .venv
```

Activate on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

# 🤝 Contributing

Contributions are welcome for legitimate security research and privacy engineering.

Good contribution areas include:

- 🧪 Additional automated tests
- 🔐 Privacy improvements
- 🛡️ Input validation
- 📊 Telemetry normalization
- 🗄️ Database reliability
- 🧹 Code quality improvements
- 📚 Documentation
- ⚡ Performance optimization
- 🧰 Safer test-environment tooling

Please avoid contributions that facilitate covert surveillance, credential theft, phishing, or unauthorized tracking.

---

# 📜 License

NanoGPS is released under the **MIT License**.

See:

```text
LICENSE
```

for the complete license text.

---

# ⚠️ Responsible Use

NanoGPS is a security research and telemetry-testing framework.

**Use it only on systems, devices, accounts, and participants for which you have explicit authorization.**

The project is not intended to facilitate:

```text
❌ Covert surveillance
❌ Unauthorized GPS tracking
❌ Credential harvesting
❌ Phishing
❌ Account impersonation
❌ Malware deployment
❌ Unauthorized device fingerprinting
❌ Collection of personal data without consent
```

Responsible security research should prioritize **consent, data minimization, isolation, and responsible disclosure**.

---

# 🌟 Project

**NanoGPS — Precision Tracker & Telemetry Profiler**

Built for:

```text
Security Research
Privacy Engineering
Browser Telemetry Analysis
Device Fingerprinting Research
Authorized Red-Team / Blue-Team Labs
Security Education
```

<p align="center">

**⚡ Analyze. Test. Measure. Secure. ⚡**

</p>
