"""
synology_client.py — async Synology DSM API client
Handles session auth and data fetching for SYNO.Core.System, Storage, Utilization,
Network, Connections, Processes, Packages, Shares, DDNS, QuickConnect, Certificates,
Syslog, FanSpeed, and File Services.
"""
import asyncio
import logging
from typing import Any
import httpx

logger = logging.getLogger(__name__)


class SynologyClient:
    """Thread-safe async Synology DSM client with session management."""

    def __init__(self, host: str, port: int, user: str, password: str, verify_ssl: bool = False):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}:{port}/webapi/entry.cgi"
        self._sid: str | None = None
        self._lock = asyncio.Lock()
        self._client = httpx.AsyncClient(verify=verify_ssl, timeout=12.0)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    async def login(self) -> None:
        """Authenticate with DSM and obtain session token (sid)."""
        async with self._lock:
            resp = await self._client.get(
                self.base_url,
                params={
                    "api": "SYNO.API.Auth",
                    "version": "7",
                    "method": "login",
                    "account": self.user,
                    "passwd": self.password,
                    "session": "NasDashboard",
                    "format": "sid",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                err_code = data.get("error", {}).get("code")
                raise RuntimeError(f"Login failed (error code {err_code})")
            self._sid = data["data"]["sid"]

    async def logout(self) -> None:
        """Terminate the current DSM session."""
        if self._sid:
            try:
                await self._client.get(
                    self.base_url,
                    params={
                        "api": "SYNO.API.Auth",
                        "version": "7",
                        "method": "logout",
                        "session": "NasDashboard",
                        "_sid": self._sid,
                    },
                )
            except Exception:
                pass
            finally:
                self._sid = None

    async def _ensure_session(self) -> None:
        if not self._sid:
            await self.login()

    async def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute an API call, re-authenticating once on session expiry (error code 119)."""
        await self._ensure_session()
        p = dict(params)
        p["_sid"] = self._sid

        resp = await self._client.get(self.base_url, params=p)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success") and data.get("error", {}).get("code") == 119:
            # Session expired — re-login and retry once
            self._sid = None
            await self.login()
            p["_sid"] = self._sid
            resp = await self._client.get(self.base_url, params=p)
            resp.raise_for_status()
            data = resp.json()

        return data

    async def _safe_get(self, params: dict[str, Any], default: Any = None) -> Any:
        """Call API and return data dict or default on error without raising."""
        try:
            res = await self._get(params)
            if res.get("success"):
                return res.get("data", default if default is not None else {})
            return default if default is not None else {"error": res.get("error")}
        except Exception as exc:
            return default if default is not None else {"error": str(exc)}

    # ------------------------------------------------------------------
    # Telemetry Endpoints
    # ------------------------------------------------------------------
    async def get_system_info(self) -> dict[str, Any]:
        """Fetch model, DSM version, CPU, RAM, temps, uptime, system info."""
        return await self._safe_get({
            "api": "SYNO.Core.System",
            "version": "3",
            "method": "info",
        }, default={})

    async def get_system_status(self) -> dict[str, Any]:
        """Fetch overall system health status (normal, attention, etc.)."""
        return await self._safe_get({
            "api": "SYNO.Core.System.Status",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_utilization(self) -> dict[str, Any]:
        """Fetch real-time CPU, RAM, swap, network throughput, and disk I/O."""
        return await self._safe_get({
            "api": "SYNO.Core.System.Utilization",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_storage(self) -> dict[str, Any]:
        """Fetch storage pools, volumes, drive health, SMART, temperatures."""
        return await self._safe_get({
            "api": "SYNO.Storage.CGI.Storage",
            "version": "1",
            "method": "load_info",
        }, default={})

    async def get_network(self) -> dict[str, Any]:
        """Fetch network interfaces, IP addresses, gateways, DNS."""
        return await self._safe_get({
            "api": "SYNO.Core.Network",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_connections(self) -> dict[str, Any]:
        """Fetch current active user connections (SMB, SSH, HTTP, AFP)."""
        return await self._safe_get({
            "api": "SYNO.Core.CurrentConnection",
            "version": "1",
            "method": "list",
        }, default={})

    async def get_processes(self) -> dict[str, Any]:
        """Fetch system processes and process group resource consumption."""
        res = await self._safe_get({
            "api": "SYNO.Core.System.ProcessGroup",
            "version": "1",
            "method": "list",
        }, default=None)
        if res is not None and not res.get("error"):
            return res
        return await self._safe_get({
            "api": "SYNO.Core.Process",
            "version": "1",
            "method": "list",
        }, default={})

    async def get_packages(self) -> dict[str, Any]:
        """Fetch installed packages and running services."""
        return await self._safe_get({
            "api": "SYNO.Core.Package",
            "version": "1",
            "method": "list",
            "additional": '["status","description","version"]',
        }, default={})

    async def get_shares(self) -> dict[str, Any]:
        """Fetch shared folders and storage volume mount points."""
        return await self._safe_get({
            "api": "SYNO.Core.Share",
            "version": "1",
            "method": "list",
        }, default={})

    async def get_certificates(self) -> dict[str, Any]:
        """Fetch installed SSL certificates, issuer, and domain names."""
        return await self._safe_get({
            "api": "SYNO.Core.Certificate.CRT",
            "version": "1",
            "method": "list",
        }, default={})

    async def get_ddns(self) -> dict[str, Any]:
        """Fetch Synology DDNS domain records, external IP, and heartbeat status."""
        return await self._safe_get({
            "api": "SYNO.Core.DDNS.Record",
            "version": "1",
            "method": "list",
        }, default={})

    async def get_quickconnect(self) -> dict[str, Any]:
        """Fetch QuickConnect ID, region, and server alias."""
        return await self._safe_get({
            "api": "SYNO.Core.QuickConnect",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_logs(self) -> dict[str, Any]:
        """Fetch recent system event logs, error and warning counts."""
        return await self._safe_get({
            "api": "SYNO.Core.SyslogClient.Log",
            "version": "1",
            "method": "list",
            "limit": 25,
            "offset": 0,
        }, default={})

    async def get_fanspeed(self) -> dict[str, Any]:
        """Fetch hardware fan mode and thermal status."""
        return await self._safe_get({
            "api": "SYNO.Core.Hardware.FanSpeed",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_smb(self) -> dict[str, Any]:
        """Fetch SMB file service configuration."""
        return await self._safe_get({
            "api": "SYNO.Core.FileServ.SMB",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_docker_containers(self) -> dict[str, Any]:
        """Fetch Docker / Container Manager container list if available."""
        res = await self._safe_get({
            "api": "SYNO.ContainerManager.Container",
            "version": "1",
            "method": "list",
            "limit": 50,
            "offset": 0,
        }, default=None)
        if res is not None and not res.get("error"):
            return res

        return await self._safe_get({
            "api": "SYNO.Docker.Container",
            "version": "1",
            "method": "list",
            "limit": 50,
            "offset": 0,
        }, default={})

    async def get_ups(self) -> dict[str, Any]:
        """Fetch UPS battery and load status."""
        return await self._safe_get({
            "api": "SYNO.Core.Hardware.UPS",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_security_scan(self) -> dict[str, Any]:
        """Fetch Synology Security Advisor scan results and rule status."""
        return await self._safe_get({
            "api": "SYNO.Core.SecurityScan.Status",
            "version": "1",
            "method": "system_get",
        }, default={})

    async def get_security_autoblock(self) -> dict[str, Any]:
        """Fetch IP Auto-Block protection configuration."""
        return await self._safe_get({
            "api": "SYNO.Core.Security.AutoBlock",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_ftp(self) -> dict[str, Any]:
        """Fetch FTP service configuration."""
        return await self._safe_get({
            "api": "SYNO.Core.FileServ.FTP",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_users(self) -> dict[str, Any]:
        """Fetch local users list and account details."""
        return await self._safe_get({
            "api": "SYNO.Core.User",
            "version": "1",
            "method": "list",
            "limit": 100,
        }, default={})

    async def get_autoblock_rules(self) -> dict[str, Any]:
        """Fetch banned / blocked IP addresses list from Auto-Block blacklist."""
        return await self._safe_get({
            "api": "SYNO.Core.Security.AutoBlock.Rules",
            "version": "1",
            "method": "list",
            "limit": 100,
        }, default={})

    async def get_dsm_web_config(self) -> dict[str, Any]:
        """Fetch DSM Web/HTTPS redirection and security headers configuration."""
        return await self._safe_get({
            "api": "SYNO.Core.Web.DSM",
            "version": "1",
            "method": "get",
        }, default={})

    async def get_password_policy(self) -> dict[str, Any]:
        """Fetch DSM password complexity, expiration, and lockout policy."""
        return await self._safe_get({
            "api": "SYNO.Core.User.PasswordPolicy",
            "version": "1",
            "method": "get",
        }, default={})

    async def aclose(self) -> None:
        """Close HTTP client session."""
        await self._client.aclose()
