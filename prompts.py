"""
Test prompts configuration for MCP accuracy benchmarking.

This file contains all test prompts organized by data source, along with
the expected answers and which MCP providers support each test.

Structure:
- Each data source (CRM, Project Management, Data Warehouse, ERP) has multiple test prompts
- Each prompt specifies which MCP providers can be tested against
- Expected answers are provided for accuracy verification
"""

# Test prompts organized by data source
TEST_PROMPTS = {
    # =========================================================================
    # CRM TEST PROMPTS
    # =========================================================================
    "crm": [
        {
            "id": "crm_deals_count",
            "prompt": "Using my CRM connection, tell me how many deals I have set to close this quarter.",
            "expected_answer": "1",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "read",
            "notes": "Tests deal filtering by close date"
        },
        {
            "id": "crm_find_contact",
            "prompt": "Using my CRM connection, find contacts named John Smith and show their email and phone number.",
            "expected_answer": "Email: test@test.com, Phone: +15127777777",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "read",
            "notes": "Tests contact search and field retrieval"
        },
        {
            "id": "crm_list_deals",
            "prompt": "Using my CRM connection, list all deals associated with Acme Corp and include the deal name, amount, and close date.",
            "expected_answer": "Deal Name: Acme Corp Deal",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "read",
            "notes": "Tests deal-company association and multi-field retrieval"
        },
        {
            "id": "crm_update_deal",
            "prompt": "Using my CRM connection, change the deal Acme Corp Deal to the stage contract sent.",
            "expected_answer": "successful",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "write",
            "notes": "Tests deal stage update operation"
        },
    ],

    # =========================================================================
    # PROJECT MANAGEMENT TEST PROMPTS
    # =========================================================================
    "proj_mgmt": [
        {
            "id": "proj_mgmt_issues_by_assignee",
            "prompt": "Using my project management connection, list all issues assigned to Alex Johnson that are in To do status.",
            "expected_answer": "2",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "read",
            "notes": "Tests issue filtering by assignee and status"
        },
        {
            "id": "proj_mgmt_backlog_issues",
            "prompt": "Using my project management connection, list the issues in the 'Acme Project' project that are in the backlog.",
            "expected_answer": "6",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "read",
            "notes": "Tests project-specific backlog query"
        },
        {
            "id": "proj_mgmt_sprint_issues",
            "prompt": "Using my project management connection, find all issues in the Sprint 112 for the Acme Project project, sorted by Highest priority.",
            "expected_answer": "PROJ-17125, PROJ-15834, PROJ-15172",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "read",
            "notes": "Tests sprint filtering with priority sorting"
        },
        {
            "id": "proj_mgmt_move_issue",
            "prompt": "Using my project management connection, move issue PROJ-14394 to In Progress.",
            "expected_answer": "Updated",
            "providers": ["connectai", "crm_native", "ipaas", "mcp_gateway", "unified_api"],
            "category": "write",
            "notes": "Tests issue status transition"
        },
    ],

    # =========================================================================
    # DATA WAREHOUSE TEST PROMPTS
    # =========================================================================
    "data_warehouse": [
        {
            "id": "data_warehouse_show_tables",
            "prompt": "Using my data warehouse connection, show me all tables in the SALESDB schema.",
            "expected_answer": "2",
            "providers": ["connectai", "ipaas"],
            "category": "read",
            "notes": "Tests schema introspection"
        },
        {
            "id": "data_warehouse_top_orders",
            "prompt": "Using my data warehouse connection, get the top 10 orders by amount from SALESDB.ORDERS.",
            "expected_answer": "ordered by amount",
            "providers": ["connectai", "ipaas"],
            "category": "read",
            "notes": "Tests ORDER BY with LIMIT"
        },
        {
            "id": "data_warehouse_recent_orders",
            "prompt": "Using my data warehouse connection, find all orders created in the last 30 days.",
            "expected_answer": "6",
            "providers": ["connectai", "ipaas"],
            "category": "read",
            "notes": "Tests date filtering (uses CREATED_DATE not ORDER_DATE)"
        },
        {
            "id": "data_warehouse_update_order",
            "prompt": "Using my data warehouse connection, update the status of order 12345 to SHIPPED in SALESDB.ORDERS.",
            "expected_answer": "Done",
            "providers": ["connectai", "ipaas"],
            "category": "write",
            "notes": "Tests UPDATE operation"
        },
    ],

    # =========================================================================
    # ERP TEST PROMPTS
    # =========================================================================
    "erp": [
        {
            "id": "erp_income_accounts",
            "prompt": "Using my ERP connection, give me the account numbers and account names for all accounts where account type is Income.",
            "expected_answer": "list of income accounts",
            "providers": ["connectai", "erp_native", "ipaas"],
            "category": "read",
            "notes": "Tests account filtering by type"
        },
        {
            "id": "erp_bins",
            "prompt": "Using my ERP connection, give me the bin number and last modified date for bins for id starting from 1 to 10.",
            "expected_answer": "list of bins",
            "providers": ["connectai", "erp_native", "ipaas"],
            "category": "read",
            "notes": "Tests ID range filtering"
        },
        {
            "id": "erp_charges",
            "prompt": "Using my ERP connection, list all the charges with id and description in a table.",
            "expected_answer": "table of charges",
            "providers": ["connectai", "erp_native", "ipaas"],
            "category": "read",
            "notes": "Tests basic listing with specific fields"
        },
        {
            "id": "erp_timezones",
            "prompt": "Using my ERP connection, give the time zones for country with id BH and CC.",
            "expected_answer": "time zones for BH and CC",
            "providers": ["connectai", "erp_native", "ipaas"],
            "category": "read",
            "notes": "Tests filtering by country ID"
        },
    ],
}

# MCP Provider metadata
MCP_PROVIDERS = {
    "connectai": {
        "name": "CData Connect AI",
        "description": "Universal connector supporting CRM, Project Management, Data Warehouse, ERP and 100+ data sources",
        "auth_type": "basic",
        "supports": ["crm", "proj_mgmt", "data_warehouse", "erp"]
    },
    "crm_native": {
        "name": "CRM Native MCP",
        "description": "Native CRM MCP server",
        "auth_type": "bearer",
        "supports": ["crm"]
    },
    "ipaas": {
        "name": "iPaaS Provider",
        "description": "iPaaS platform MCP integration",
        "auth_type": "url_token",
        "supports": ["crm", "proj_mgmt", "data_warehouse"]
    },
    "mcp_gateway": {
        "name": "MCP Gateway",
        "description": "MCP gateway service",
        "auth_type": "url_token",
        "supports": ["crm", "proj_mgmt"]
    },
    "unified_api": {
        "name": "Unified API",
        "description": "Unified API provider with MCP support",
        "auth_type": "stdio",
        "supports": ["crm", "proj_mgmt"]
    },
    "erp_native": {
        "name": "ERP Native MCP",
        "description": "Native ERP MCP server (if available)",
        "auth_type": "bearer",
        "supports": ["erp"]
    },
}


def get_prompts_for_provider(provider: str) -> list:
    """Get all test prompts that can be run against a specific provider."""
    prompts = []
    for data_source, source_prompts in TEST_PROMPTS.items():
        for prompt in source_prompts:
            if provider in prompt["providers"]:
                prompts.append({
                    **prompt,
                    "data_source": data_source
                })
    return prompts


def get_prompts_for_data_source(data_source: str) -> list:
    """Get all test prompts for a specific data source."""
    return TEST_PROMPTS.get(data_source, [])


def get_all_prompts() -> list:
    """Get all test prompts with their data source."""
    prompts = []
    for data_source, source_prompts in TEST_PROMPTS.items():
        for prompt in source_prompts:
            prompts.append({
                **prompt,
                "data_source": data_source
            })
    return prompts


def get_prompt_by_id(prompt_id: str) -> dict:
    """Get a specific prompt by its ID."""
    for data_source, source_prompts in TEST_PROMPTS.items():
        for prompt in source_prompts:
            if prompt["id"] == prompt_id:
                return {**prompt, "data_source": data_source}
    return None


def list_all_prompt_ids() -> list:
    """List all available prompt IDs."""
    ids = []
    for source_prompts in TEST_PROMPTS.values():
        for prompt in source_prompts:
            ids.append(prompt["id"])
    return ids


if __name__ == "__main__":
    # Print summary of test prompts
    print("=" * 80)
    print("MCP ACCURACY TEST PROMPTS SUMMARY")
    print("=" * 80)

    for data_source, prompts in TEST_PROMPTS.items():
        print(f"\n{data_source.upper()} ({len(prompts)} prompts):")
        for prompt in prompts:
            print(f"  - {prompt['id']}: {prompt['prompt'][:60]}...")
            print(f"    Providers: {', '.join(prompt['providers'])}")

    print("\n" + "=" * 80)
    print("PROVIDER COVERAGE")
    print("=" * 80)

    for provider, info in MCP_PROVIDERS.items():
        prompts = get_prompts_for_provider(provider)
        print(f"\n{info['name']} ({provider}):")
        print(f"  Supports: {', '.join(info['supports'])}")
        print(f"  Total test prompts: {len(prompts)}")
