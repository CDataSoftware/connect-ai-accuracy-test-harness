"""
Configuration settings for the LangChain MCP testing harness.
Supports multiple MCP providers and data sources for accuracy benchmarking.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for MCP LangChain integration"""

    # MCP Server Selection
    MCP_SERVER_TYPE: str = os.getenv("MCP_SERVER_TYPE", "connectai")

    # MCP Server Configurations
    # Each server can connect to multiple data sources (CRM, Project Management, Data Warehouse, ERP)
    MCP_SERVERS = {
        # CData Connect AI - Basic Authentication (username:PAT)
        "connectai": {
            "url": os.getenv("CONNECTAI_MCP_URL", "https://mcp.cloud.cdata.com/mcp"),
            "auth_type": "basic",
            "transport": "streamable_http"
        },
        # CRM Native MCP Server
        "crm_native": {
            "url": os.getenv("CRM_NATIVE_MCP_URL", ""),
            "auth_type": "bearer",
            "transport": "streamable_http"
        },
        # ERP Native MCP Server
        "erp_native": {
            "url": os.getenv("ERP_NATIVE_MCP_URL", ""),
            "auth_type": "bearer",
            "transport": "streamable_http"
        },
        # iPaaS Provider MCP Server (URL contains embedded auth token)
        "ipaas": {
            "url": os.getenv("IPAAS_MCP_URL", ""),
            "auth_type": "none",
            "transport": "streamable_http"
        },
        # MCP Gateway Server (URL contains instance ID)
        "mcp_gateway": {
            "url": os.getenv("MCP_GATEWAY_URL", ""),
            "auth_type": "none",
            "transport": "streamable_http"
        },
        # Unified API MCP Server - stdio transport via npx
        "unified_api": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote@latest",
                os.getenv("UNIFIED_API_MCP_URL", ""),
                "--header",
                f"Authorization: Bearer {os.getenv('UNIFIED_API_AUTH_TOKEN', '')}"
            ],
            "auth_type": "stdio",
            "transport": "stdio"
        },
    }

    # LLM Configuration
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.2"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-5")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # HTTP Configuration
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # CData Connect AI - Basic Auth (base64 encoded username:PAT)
    CONNECTAI_AUTH: str = os.getenv("CONNECTAI_AUTH", "")

    # CRM Native MCP Authentication
    CRM_NATIVE_BEARER_TOKEN: str = os.getenv("CRM_NATIVE_BEARER_TOKEN", "")

    # ERP Native MCP Authentication
    ERP_NATIVE_BEARER_TOKEN: str = os.getenv("ERP_NATIVE_BEARER_TOKEN", "")

    # Unified API Authentication
    UNIFIED_API_AUTH_TOKEN: str = os.getenv("UNIFIED_API_AUTH_TOKEN", "")

    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration as dictionary"""
        return {
            "temperature": cls.DEFAULT_TEMPERATURE,
            "max_tokens": cls.DEFAULT_MAX_TOKENS,
            "model": cls.DEFAULT_MODEL
        }

    @classmethod
    def get_current_server_config(cls) -> dict:
        """Get configuration for the currently selected MCP server"""
        server_type = cls.MCP_SERVER_TYPE.lower()
        if server_type not in cls.MCP_SERVERS:
            raise ValueError(f"Unknown MCP server type: {server_type}. Must be one of: {list(cls.MCP_SERVERS.keys())}")
        return cls.MCP_SERVERS[server_type]

    @classmethod
    def get_server_config(cls, server_type: str) -> dict:
        """Get configuration for a specific MCP server type"""
        server_type = server_type.lower()
        if server_type not in cls.MCP_SERVERS:
            raise ValueError(f"Unknown MCP server type: {server_type}. Must be one of: {list(cls.MCP_SERVERS.keys())}")
        return cls.MCP_SERVERS[server_type]

    @classmethod
    def get_auth_headers(cls, server_type: str = None) -> dict:
        """Get authentication headers for the specified or current MCP server"""
        if server_type:
            server_config = cls.get_server_config(server_type)
        else:
            server_config = cls.get_current_server_config()
            server_type = cls.MCP_SERVER_TYPE.lower()

        auth_type = server_config["auth_type"]

        if auth_type == "bearer":
            if server_type == "crm_native":
                if not cls.CRM_NATIVE_BEARER_TOKEN:
                    raise ValueError("CRM_NATIVE_BEARER_TOKEN environment variable is required")
                return {"Authorization": f"Bearer {cls.CRM_NATIVE_BEARER_TOKEN}"}
            elif server_type == "erp_native":
                if not cls.ERP_NATIVE_BEARER_TOKEN:
                    raise ValueError("ERP_NATIVE_BEARER_TOKEN environment variable is required")
                return {"Authorization": f"Bearer {cls.ERP_NATIVE_BEARER_TOKEN}"}
            else:
                raise ValueError(f"No bearer token configured for server type: {server_type}")
        elif auth_type == "basic":
            if not cls.CONNECTAI_AUTH:
                raise ValueError("CONNECTAI_AUTH environment variable is required")
            return {"Authorization": f"Basic {cls.CONNECTAI_AUTH}"}
        elif auth_type == "none":
            # No additional auth headers (auth embedded in URL)
            return {}
        elif auth_type == "stdio":
            # stdio transport doesn't use HTTP headers
            return {}
        else:
            raise ValueError(f"Unknown auth type: {auth_type}")

    @classmethod
    def validate_config(cls, server_type: str = None) -> bool:
        """Validate that all required configuration is present for the specified server"""
        if server_type is None:
            server_type = cls.MCP_SERVER_TYPE.lower()
        else:
            server_type = server_type.lower()

        server_config = cls.get_server_config(server_type)

        if server_type == "connectai":
            if not cls.CONNECTAI_AUTH:
                raise ValueError("CONNECTAI_AUTH is required for CData Connect AI")
        elif server_type == "crm_native":
            if not cls.CRM_NATIVE_BEARER_TOKEN:
                raise ValueError("CRM_NATIVE_BEARER_TOKEN is required for CRM Native MCP server")
        elif server_type == "erp_native":
            if not cls.ERP_NATIVE_BEARER_TOKEN:
                raise ValueError("ERP_NATIVE_BEARER_TOKEN is required for ERP Native MCP server")
        elif server_type == "ipaas":
            if not server_config.get("url"):
                raise ValueError("IPAAS_MCP_URL is required for iPaaS MCP server")
        elif server_type == "mcp_gateway":
            if not server_config.get("url"):
                raise ValueError("MCP_GATEWAY_URL is required for MCP Gateway server")
        elif server_type == "unified_api":
            if not cls.UNIFIED_API_AUTH_TOKEN:
                raise ValueError("UNIFIED_API_AUTH_TOKEN is required for Unified API MCP server")

        return True

    @classmethod
    def list_available_servers(cls) -> list:
        """List all configured MCP server types"""
        return list(cls.MCP_SERVERS.keys())
