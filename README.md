# LLM Tool-Use Accuracy Testing Harness

A benchmarking framework for measuring LLM accuracy in autonomous tool-use scenarios. This harness was developed to produce data for research on AI agent performance when interacting with external systems via the Model Context Protocol (MCP).

## Research Context

This project implements a **ReAct (Reasoning + Acting) agent pattern** to test how well large language models can:

1. **Reason** about what information they need to answer a question
2. **Select** appropriate tools from available MCP server endpoints
3. **Execute** tool calls with correct parameters
4. **Interpret** results and iterate until the question is answered
5. **Synthesize** accurate final responses

The harness captures comprehensive metrics including token usage, API costs, execution time, and tool call patterns—enabling quantitative analysis of LLM accuracy and efficiency.

## Test Matrix

The harness tests **16 prompts** across **4 data sources** using **5 MCP providers**:

### Data Sources & Prompts

| Data Source | # Prompts | Test Categories |
|-------------|-----------|-----------------|
| CRM | 4 | Deals count, contact search, deal listing, deal updates |
| Project Management | 4 | Issue filtering, backlog queries, sprint issues, status transitions |
| Data Warehouse | 4 | Schema introspection, ORDER BY queries, date filtering, UPDATE operations |
| ERP | 4 | Account filtering, ID range queries, charge listing, timezone lookup |

### MCP Providers Tested

| Provider | Auth Type | Supported Data Sources |
|----------|-----------|----------------------|
| CData Connect AI | Basic Auth | CRM, Project Management, Data Warehouse, ERP (100+ sources) |
| CRM Native | Bearer | CRM only |
| iPaaS Provider | URL Token | CRM, Project Management, Data Warehouse |
| MCP Gateway | URL Token | CRM, Project Management |
| Unified API | stdio/Bearer | CRM, Project Management |

## Architecture

```
User Prompt
    │
    ▼
┌─────────────────────────────────────┐
│  LangGraph ReAct Agent (GPT-5)      │
│  - Reasoning loop                   │
│  - Tool selection                   │
│  - Result interpretation            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  MCP Tools (via MultiServerMCPClient)│
│  - CRM operations                   │
│  - Project management operations    │
│  - Data warehouse SQL queries       │
│  - ERP data                         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  DynamicToolLogger                  │
│  - Token counting (OpenAI API)      │
│  - Cost calculation                 │
│  - Execution timing                 │
│  - Tool call statistics             │
└─────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/CDataSoftware/connect-ai-accuracy-test-harness.git
cd connect-ai-accuracy-test-harness

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

## Quick Start

### Run a single test
```bash
python run_tests.py --provider connectai --prompt-id crm_deals_count
```

### Run all CRM tests for a provider
```bash
python run_tests.py --provider connectai --data-source crm --runs 5
```

### Run tests and export results
```bash
python run_tests.py --provider connectai --data-source proj_mgmt --runs 5 --output results.csv
```

### List available prompts and providers
```bash
python run_tests.py --list-prompts
python run_tests.py --list-providers
```

## Configuration

Edit `.env` to configure your MCP server credentials. See `.env.example` for all options.

### Required Environment Variables

**For all tests:**
```bash
OPENAI_API_KEY=your_openai_api_key
```

**For CData Connect AI (supports all data sources):**
```bash
CONNECTAI_MCP_URL=https://mcp.cloud.cdata.com/mcp
CONNECTAI_AUTH=your_base64_encoded_credentials
```
Note: `CONNECTAI_AUTH` should be base64 encoded `username:personal_access_token`

**For CRM Native:**
```bash
CRM_NATIVE_MCP_URL=https://example.com/mcp
CRM_NATIVE_BEARER_TOKEN=your_token
```

**For iPaaS Provider:**
```bash
IPAAS_MCP_URL=https://example.com/mcp
```

**For MCP Gateway:**
```bash
MCP_GATEWAY_URL=https://example.com/mcp
```

**For Unified API:**
```bash
UNIFIED_API_MCP_URL=https://example.com/mcp
UNIFIED_API_AUTH_TOKEN=your_api_key
```

## Running Tests

The `run_tests.py` script provides a unified interface for running all tests:

```bash
# Run specific prompt against specific provider
python run_tests.py --provider connectai --prompt-id crm_deals_count --runs 5

# Run all prompts for a data source
python run_tests.py --provider ipaas --data-source proj_mgmt --runs 3

# Run all available prompts for a provider
python run_tests.py --provider mcp_gateway --runs 1

# Export results to CSV
python run_tests.py --provider connectai --data-source crm --runs 5 --output crm_results.csv

# Export results to JSON
python run_tests.py --provider connectai --data-source crm --runs 5 --output crm_results.json
```

## Metrics Collected

The `DynamicToolLogger` captures:

| Metric | Description |
|--------|-------------|
| `llm_prompt_tokens` | Input tokens sent to GPT-5 |
| `llm_completion_tokens` | Output tokens generated |
| `total_tool_calls` | Number of MCP tool invocations |
| `execution_time` | End-to-end duration in seconds |
| `input_cost` | Cost at $1.25/1M tokens |
| `output_cost` | Cost at $10.00/1M tokens |
| `tools_available` | Number of tools exposed by MCP server |

### Sample Output

```
FINAL TOKEN USAGE STATISTICS
========================================
TOOL CALL STATISTICS:
   Total tool calls: 3

LLM TOKEN USAGE (from OpenAI API):
   Prompt tokens:      12,847
   Completion tokens:     892
   Total LLM tokens:   13,739

COST BREAKDOWN:
   Input cost:  $0.0161
   Output cost: $0.0089
   Total cost:  $0.0250
```

## Project Structure

```
.
├── run_tests.py            # Unified test runner
├── prompts.py              # Test prompt definitions (16 prompts)
├── config.py               # MCP provider configurations
├── logger.py               # Shared metrics logger
├── validate_config.py      # Configuration validation utility
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── LICENSE                 # MIT License
└── CLAUDE.md               # AI assistant context
```

## Test Prompts Reference

### CRM Prompts
| ID | Prompt | Category |
|----|--------|----------|
| `crm_deals_count` | How many deals set to close this quarter? | read |
| `crm_find_contact` | Find contacts named John Smith | read |
| `crm_list_deals` | List deals for Acme Corp | read |
| `crm_update_deal` | Change deal stage to contract sent | write |

### Project Management Prompts
| ID | Prompt | Category |
|----|--------|----------|
| `proj_mgmt_issues_by_assignee` | Issues assigned to user in To Do | read |
| `proj_mgmt_backlog_issues` | Issues in project backlog | read |
| `proj_mgmt_sprint_issues` | Sprint issues sorted by priority | read |
| `proj_mgmt_move_issue` | Move issue to In Progress | write |

### Data Warehouse Prompts
| ID | Prompt | Category |
|----|--------|----------|
| `data_warehouse_show_tables` | Show tables in schema | read |
| `data_warehouse_top_orders` | Top 10 orders by amount | read |
| `data_warehouse_recent_orders` | Orders in last 30 days | read |
| `data_warehouse_update_order` | Update order status | write |

### ERP Prompts
| ID | Prompt | Category |
|----|--------|----------|
| `erp_income_accounts` | Accounts where type is Income | read |
| `erp_bins` | Bins for IDs 1-10 | read |
| `erp_charges` | List all charges | read |
| `erp_timezones` | Time zones for country IDs | read |

## Reproducing Research Results

To reproduce the accuracy testing from the whitepaper:

1. **Configure credentials** for all MCP providers you want to test
2. **Run the test suite** with 5 runs per prompt:
   ```bash
   python run_tests.py --provider connectai --data-source crm --runs 5 --output connectai_crm.csv
   python run_tests.py --provider crm_native --data-source crm --runs 5 --output native_crm.csv
   python run_tests.py --provider ipaas --data-source crm --runs 5 --output ipaas_crm.csv
   ```
3. **Compare results** with expected answers in `prompts.py`
4. **Calculate accuracy** by comparing `answer` to `expected_answer`

## Dependencies

- `langchain` / `langchain-openai` - LLM orchestration
- `langgraph` - ReAct agent implementation
- `langchain_mcp_adapters` - MCP protocol integration
- `tiktoken` - Token counting
- `python-dotenv` - Environment management

## License

MIT License - See LICENSE file for details.

## Contributing

This is a research tool. Issues and pull requests are welcome for bug fixes and improvements to measurement accuracy.
