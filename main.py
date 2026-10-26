"""
main.py — FastAPI backend for Synology NAS Supercharged Geek Dashboard
"""
import os
import asyncio
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from synology_client import SynologyClient
from version import get_static_meta, fetch_github_release_info

load_dotenv()

NAS_HOST = os.getenv("NAS_HOST", "127.0.0.1")
NAS_PORT = int(os.getenv("NAS_PORT", "5001"))
NAS_USER = os.getenv("NAS_USER", "admin")
NAS_PASS = os.getenv("NAS_PASS", "")
_verify_raw = os.getenv("NAS_VERIFY_SSL", "false").lower()
NAS_VERIFY_SSL = _verify_raw not in ("false", "0", "no")

_client: SynologyClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _client
    _client = SynologyClient(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS, verify_ssl=NAS_VERIFY_SSL)
    try:
        await _client.login()
    except Exception as exc:
        print(f"[WARN] Initial NAS login failed: {exc}")
    yield
    if _client:
        try:
            await _client.logout()
        except Exception:
            pass
        await _client.aclose()


app = FastAPI(title="Synology NAS Supercharged Geek Dashboard", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Prevent browser caching of dashboard HTML and dynamic API data
    if request.url.path == "/" or request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


def get_client() -> SynologyClient:
    if _client is None:
        raise HTTPException(status_code=503, detail="NAS client not initialised")
    return _client


# ------------------------------------------------------------------
# HTML Geek Dashboard
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    meta = get_static_meta()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "dashboard_meta": meta,
            "app_version": meta["version"],
        },
    )


@app.get("/api/version")
async def api_version() -> dict[str, Any]:
    return await fetch_github_release_info()


# ------------------------------------------------------------------
# Comprehensive Supercharged Telemetry Aggregator
# ------------------------------------------------------------------
@app.get("/api/all")
async def api_all() -> dict[str, Any]:
    """Single aggregated high-speed telemetry endpoint."""
    client = get_client()
    (
        system,
        status,
        utilization,
        storage,
        network,
        connections,
        processes,
        packages,
        shares,
        certificates,
        ddns,
        quickconnect,
        logs,
        fanspeed,
        smb,
        docker,
        ups,
        security_scan,
        autoblock,
        autoblock_rules,
        ftp,
        users,
        web_config,
        password_policy,
    ) = await asyncio.gather(
        client.get_system_info(),
        client.get_system_status(),
        client.get_utilization(),
        client.get_storage(),
        client.get_network(),
        client.get_connections(),
        client.get_processes(),
        client.get_packages(),
        client.get_shares(),
        client.get_certificates(),
        client.get_ddns(),
        client.get_quickconnect(),
        client.get_logs(),
        client.get_fanspeed(),
        client.get_smb(),
        client.get_docker_containers(),
        client.get_ups(),
        client.get_security_scan(),
        client.get_security_autoblock(),
        client.get_autoblock_rules(),
        client.get_ftp(),
        client.get_users(),
        client.get_dsm_web_config(),
        client.get_password_policy(),
        return_exceptions=True,
    )

    def unpack(res: Any) -> Any:
        return res if not isinstance(res, Exception) else {"error": str(res)}

    dashboard_meta = await fetch_github_release_info()
    return {
        "app_version": dashboard_meta["version"],
        "dashboard_meta": dashboard_meta,
        "host_info": {
            "host": NAS_HOST,
            "port": NAS_PORT,
            "user": NAS_USER,
            "ssl": NAS_VERIFY_SSL,
        },
        "system": unpack(system),
        "status": unpack(status),
        "utilization": unpack(utilization),
        "storage": unpack(storage),
        "network": unpack(network),
        "connections": unpack(connections),
        "processes": unpack(processes),
        "packages": unpack(packages),
        "shares": unpack(shares),
        "certificates": unpack(certificates),
        "ddns": unpack(ddns),
        "quickconnect": unpack(quickconnect),
        "logs": unpack(logs),
        "fanspeed": unpack(fanspeed),
        "smb": unpack(smb),
        "docker": unpack(docker),
        "ups": unpack(ups),
        "security_scan": unpack(security_scan),
        "autoblock": unpack(autoblock),
        "autoblock_rules": unpack(autoblock_rules),
        "ftp": unpack(ftp),
        "users": unpack(users),
        "web_config": unpack(web_config),
        "password_policy": unpack(password_policy),
    }


@app.get("/api/system")
async def api_system() -> dict[str, Any]:
    return await get_client().get_system_info()


@app.get("/api/utilization")
async def api_utilization() -> dict[str, Any]:
    return await get_client().get_utilization()


@app.get("/api/storage")
async def api_storage() -> dict[str, Any]:
    return await get_client().get_storage()


@app.get("/api/shares")
async def api_shares() -> dict[str, Any]:
    return await get_client().get_shares()


@app.get("/api/logs")
async def api_logs() -> dict[str, Any]:
    return await get_client().get_logs()


@app.get("/api/connections")
async def api_connections() -> dict[str, Any]:
    return await get_client().get_connections()


@app.get("/api/processes")
async def api_processes() -> dict[str, Any]:
    return await get_client().get_processes()


@app.get("/api/security")
async def api_security() -> dict[str, Any]:
    """Dedicated Security & Hardening Advisor telemetry endpoint."""
    client = get_client()
    (
        sec_scan,
        autoblock,
        autoblock_rules,
        ftp,
        users,
        certs,
        shares,
        smb,
        web_config,
        password_policy,
    ) = await asyncio.gather(
        client.get_security_scan(),
        client.get_security_autoblock(),
        client.get_autoblock_rules(),
        client.get_ftp(),
        client.get_users(),
        client.get_certificates(),
        client.get_shares(),
        client.get_smb(),
        client.get_dsm_web_config(),
        client.get_password_policy(),
        return_exceptions=True,
    )

    def unpack(res: Any) -> Any:
        return res if not isinstance(res, Exception) else {"error": str(res)}

    return {
        "security_scan": unpack(sec_scan),
        "autoblock": unpack(autoblock),
        "autoblock_rules": unpack(autoblock_rules),
        "ftp": unpack(ftp),
        "users": unpack(users),
        "certificates": unpack(certs),
        "shares": unpack(shares),
        "smb": unpack(smb),
        "web_config": unpack(web_config),
        "password_policy": unpack(password_policy),
    }


@app.get("/api/packages")
async def api_packages() -> dict[str, Any]:
    return await get_client().get_packages()
