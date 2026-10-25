# 🚀 Synology DSM Supercharged Geek Telemetry HUD & Security Advisor

A real-time, high-density telemetry dashboard and security hardening advisor for **Synology NAS** (DS920+ / DSM 7.x). Built with **FastAPI**, **Jinja2**, and **Vanilla JavaScript / 60 FPS HTML5 Canvas** without bulky front-end framework dependencies.

![Synology Geek Dashboard](https://img.shields.io/badge/Synology-DSM%207.3-0284c7?style=for-the-badge&logo=synology&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed?style=for-the-badge&logo=docker&logoColor=white)

---

## ⚡ Features

### 🖥️ Real-Time Hardware & Kernel Telemetry
- **60 FPS Canvas Sparklines**: Real-time graphs for CPU Load, RAM & Buffer Cache, Network Inbound (RX) / Outbound (TX), and Disk Read/Write throughput & IOPS.
- **Multi-Core CPU Load Breakdown**: Per-core utilization gauge across all physical cores.
- **Physical Drive Bays Enclosure HUD**: 4-Bay enclosure visualization showing drive temps, vendor/model, storage pool assignment, and clickable S.M.A.R.T diagnostic modal.
- **Storage Pools & Btrfs Volumes**: Real-time capacity breakdown, filesystem type, and SHR RAID health status.
- **Network Interfaces & Cloud Access**: Gigabit LAN interfaces, active IP assignments, throughput, Synology DDNS status, and QuickConnect relay telemetry.
- **Active Connections & Audit**: Live SMB, HTTP/HTTPS, and service sessions with client IPs and protocols.
- **DSM Services & Process Slices**: Top system services, PIDs, memory allocation, and CPU load.
- **Live System Audit Logs**: Real-time DSM event log streamer with severity badges (INFO, WARN, ERROR).

### 🛡️ Security & Hardening Advisor
- **Dynamic Posture Score (0–100%)**: Real-time hardening score ring with status badges (*HARDENED / SECURE*, *ELEVATED RISK*, *CRITICAL ACTION NEEDED*).
- **DSM Security Advisor Scanner Breakdown**: Status tracking across Malware, Network Firewall, System Integrity, Account Security, and Firmware Updates.
- **Hardening Checklist & Remediation Matrix**:
  - 🚨 Default `admin` account status and disablement recommendations.
  - 🚨 2-Factor Authentication (2FA/OTP) enforcement across administrative accounts.
  - ⚠️ Shared folder data-at-rest encryption check (AES-256).
  - ⚠️ Drive thermal operating threshold alerts.
  - ⚠️ Firmware & Package updates check.
  - ✅ IP Auto-Block protection policies and threshold tracking.
  - ✅ Insecure service audits (FTP port 21, Telnet, SSH, SMB3/NTLMv1).
- **User Accounts & Privileges Audit Matrix**: Role tiers and security status for all local DSM users.
- **SSL/TLS Certificates**: Expiry countdown, issuer, and domain coverage (Let's Encrypt / DDNS / QuickConnect).

---

## 🛠️ Quick Start

### Option 1: Run Locally (Python 3.11+)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rbaronia/synology-geek-dashboard.git
   cd synology-geek-dashboard
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   NAS_HOST=10.0.0.91        # IP or hostname of your Synology NAS
   NAS_PORT=5001             # DSM HTTPS port (5001) or HTTP (5000)
   NAS_USER=your_dsm_user    # DSM user account
   NAS_PASS=your_dsm_pass    # DSM user password
   NAS_VERIFY_SSL=false      # Set to false for self-signed certificates
   ```

4. **Start the application**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. Open your browser at **`http://localhost:8000`**.

---

### Option 2: Run with Docker / Synology Container Manager

1. **Run via Docker Compose**:
   ```bash
   docker compose up -d --build
   ```

2. **Run via Docker CLI**:
   ```bash
   docker build -t synology-dashboard .
   docker run -d \
     --name synology-dashboard \
     -p 8000:8000 \
     -e NAS_HOST=10.0.0.91 \
     -e NAS_PORT=5001 \
     -e NAS_USER=admin \
     -e NAS_PASS=your_password \
     -e NAS_VERIFY_SSL=false \
     synology-dashboard
   ```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Main Supercharged Geek Dashboard HUD |
| `/api/all` | `GET` | High-speed aggregated telemetry feed |
| `/api/security` | `GET` | Security & Hardening Advisor telemetry |
| `/api/system` | `GET` | DSM System and hardware telemetry |
| `/api/utilization` | `GET` | Real-time CPU, RAM, Network & Disk I/O |
| `/api/storage` | `GET` | Storage pools, volumes, drives & SMART |
| `/api/connections`| `GET` | Active user sessions and client connections |
| `/api/shares` | `GET` | Shared folder paths and encryption status |
| `/api/processes` | `GET` | Running services, daemons, and PIDs |
| `/api/logs` | `GET` | Recent DSM system event and audit logs |

---

## 📄 License

MIT License. Designed with ⚡ for Synology DSM power users and homelab engineers.
