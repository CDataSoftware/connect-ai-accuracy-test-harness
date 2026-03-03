#!/usr/bin/env python3
"""
Test script to verify MCP server configuration
"""

import os
from config import Config

def test_config():
    """Test the MCP server configuration"""
    print("🔍 Testing MCP Server Configuration")
    print("=" * 50)
    
    # Show all environment variables related to MCP
    print("\n📋 Environment Variables:")
    mcp_vars = [
        'MCP_SERVER_TYPE', 'CONNECTAI_MCP_URL', 'CONNECTAI_AUTH',
        'CRM_NATIVE_MCP_URL', 'CRM_NATIVE_BEARER_TOKEN',
        'ERP_NATIVE_MCP_URL', 'ERP_NATIVE_BEARER_TOKEN',
        'IPAAS_MCP_URL', 'MCP_GATEWAY_URL',
        'UNIFIED_API_MCP_URL', 'UNIFIED_API_AUTH_TOKEN'
    ]
    
    for var in mcp_vars:
        value = os.getenv(var, 'NOT SET')
        if 'TOKEN' in var or 'KEY' in var:
            # Mask sensitive values
            if value != 'NOT SET' and len(value) > 4:
                value = '***' + value[-4:]
        print(f"   {var}: {value}")
    
    print("\n🔧 Configuration Analysis:")
    try:
        # Test server configuration
        server_config = Config.get_current_server_config()
        print(f"   Selected Server: {Config.MCP_SERVER_TYPE}")
        print(f"   Server URL: {server_config['url']}")
        print(f"   Auth Type: {server_config['auth_type']}")
        print(f"   Transport: {server_config['transport']}")
        
        # Test validation
        Config.validate_config()
        print("   ✅ Configuration validation passed")
        
        # Test auth headers
        auth_headers = Config.get_auth_headers()
        if auth_headers:
            print(f"   Auth Headers: {list(auth_headers.keys())}")
        else:
            print("   Auth Headers: None (auth embedded in URL or uses stdio transport)")
            
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    print("\n✅ Configuration test completed successfully!")
    return True

if __name__ == "__main__":
    test_config()

