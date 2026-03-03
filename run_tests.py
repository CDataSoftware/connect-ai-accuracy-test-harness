#!/usr/bin/env python3
"""
Unified test runner for MCP accuracy benchmarking.

This script runs test prompts against specified MCP providers and collects
metrics for accuracy analysis. Results can be output in various formats
for comparison with the research spreadsheet.

Usage:
    python run_tests.py --provider connectai --data-source crm
    python run_tests.py --provider connectai --prompt-id crm_deals_count --runs 5
    python run_tests.py --all-providers --data-source proj_mgmt --runs 3
    python run_tests.py --list-prompts
"""

import asyncio
import argparse
import csv
import json
import os
import sys
import time
import datetime
from collections import defaultdict
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from config import Config
from logger import DynamicToolLogger
from prompts import (
    TEST_PROMPTS,
    MCP_PROVIDERS,
    get_prompts_for_provider,
    get_prompts_for_data_source,
    get_prompt_by_id,
    get_all_prompts,
    list_all_prompt_ids,
)


class TestRunner:
    """Runs MCP accuracy tests and collects metrics."""

    def __init__(self, model: str = "gpt-5", temperature: float = 0.2):
        self.model = model
        self.temperature = temperature
        self.results = []

    async def create_mcp_client(self, provider: str) -> MultiServerMCPClient:
        """Create an MCP client for the specified provider."""
        server_config = Config.get_server_config(provider)
        Config.validate_config(provider)

        if server_config["transport"] == "stdio":
            # stdio transport (e.g., Merge AI)
            return MultiServerMCPClient(
                connections={
                    "default": {
                        "transport": "stdio",
                        "command": server_config["command"],
                        "args": server_config["args"],
                    }
                }
            )
        else:
            # HTTP transport
            headers = {}
            if server_config["auth_type"] in ["bearer", "basic"]:
                headers = Config.get_auth_headers(provider)

            return MultiServerMCPClient(
                connections={
                    "default": {
                        "transport": server_config["transport"],
                        "url": server_config["url"],
                        "headers": headers,
                    }
                }
            )

    async def run_single_test(
        self,
        provider: str,
        prompt: str,
        prompt_id: str,
    ) -> dict:
        """Run a single test and return metrics."""
        result = {
            "prompt_id": prompt_id,
            "provider": provider,
            "prompt": prompt,
            "answer": None,
            "correct": None,
            "time_seconds": None,
            "tool_call_count": 0,
            "token_count": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "error": None,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Create logger outside try block so we can capture metrics even on failure
        logger = DynamicToolLogger(model_name=self.model)
        start_time = time.time()

        try:
            # Create MCP client
            mcp_client = await self.create_mcp_client(provider)

            # Get tools from MCP server
            tools = await mcp_client.get_tools()
            result["tools_available"] = len(tools)

            # Create agent
            llm = ChatOpenAI(model=self.model, temperature=self.temperature)
            agent = create_react_agent(llm, tools)

            # Run the test
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config={"callbacks": [logger]}
            )

            # Extract results
            result["answer"] = response["messages"][-1].content
            result["tool_call_count"] = logger.tool_call_count
            result["prompt_tokens"] = logger.llm_prompt_tokens
            result["completion_tokens"] = logger.llm_completion_tokens
            result["token_count"] = logger.llm_total_tokens

        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error running test: {e}")

        finally:
            # Always capture metrics, even on failure
            end_time = time.time()
            result["time_seconds"] = round(end_time - start_time, 2)

            # Validate that MCP tools were actually used
            # If LLM answered without calling any tools, it used training data instead of MCP server
            if result["answer"] and result["tool_call_count"] == 0 and not result["error"]:
                result["error"] = "LLM answered from training data without using MCP tools"
                result["answer"] = None  # Clear the answer since it didn't come from MCP

        return result

    async def run_test_suite(
        self,
        provider: str,
        prompts: list,
        runs_per_test: int = 1,
        verbose: bool = True,
    ) -> list:
        """Run a suite of tests with multiple runs per prompt."""
        all_results = []

        for prompt_info in prompts:
            prompt_id = prompt_info["id"]
            prompt_text = prompt_info["prompt"]

            if verbose:
                print(f"\n{'='*60}")
                print(f"Testing: {prompt_id}")
                print(f"Provider: {provider}")
                print(f"Prompt: {prompt_text[:80]}...")
                print(f"{'='*60}")

            for run_num in range(1, runs_per_test + 1):
                if verbose:
                    print(f"\n  Run {run_num}/{runs_per_test}...")

                result = await self.run_single_test(
                    provider=provider,
                    prompt=prompt_text,
                    prompt_id=prompt_id,
                )
                result["run"] = run_num
                result["expected_answer"] = prompt_info.get("expected_answer", "")
                result["data_source"] = prompt_info.get("data_source", "")

                all_results.append(result)

                if verbose:
                    if result["error"]:
                        print(f"    ❌ Error: {result['error']}")
                    else:
                        print(f"    ✓ Time: {result['time_seconds']}s")
                        print(f"    ✓ Tool calls: {result['tool_call_count']}")
                        print(f"    ✓ Tokens: {result['token_count']}")
                        answer_preview = str(result['answer'])[:100]
                        print(f"    ✓ Answer: {answer_preview}...")

        self.results.extend(all_results)
        return all_results

    def export_results_csv(self, filename: str):
        """Export results to CSV file."""
        if not self.results:
            print("No results to export")
            return

        fieldnames = [
            "prompt_id", "data_source", "provider", "run",
            "answer", "expected_answer", "correct",
            "time_seconds", "tool_call_count", "token_count",
            "prompt_tokens", "completion_tokens", "tools_available",
            "error", "timestamp"
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.results)

        print(f"Results exported to: {filename}")

    def export_results_json(self, filename: str):
        """Export results to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"Results exported to: {filename}")

    def print_summary(self):
        """Print a summary of test results."""
        if not self.results:
            print("No results to summarize")
            return

        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)

        # Group by provider and prompt
        by_provider = defaultdict(list)
        for r in self.results:
            by_provider[r["provider"]].append(r)

        for provider, results in by_provider.items():
            successful = [r for r in results if not r.get("error")]
            failed = [r for r in results if r.get("error")]

            print(f"\n{provider.upper()}:")
            print(f"  Total runs: {len(results)}")
            print(f"  Successful: {len(successful)}")
            print(f"  Failed: {len(failed)}")

            if successful:
                avg_time = sum(r["time_seconds"] for r in successful) / len(successful)
                avg_tokens = sum(r["token_count"] for r in successful) / len(successful)
                avg_tools = sum(r["tool_call_count"] for r in successful) / len(successful)
                print(f"  Avg time: {avg_time:.2f}s")
                print(f"  Avg tokens: {avg_tokens:.0f}")
                print(f"  Avg tool calls: {avg_tools:.1f}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run MCP accuracy tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --provider connectai --data-source crm
  python run_tests.py --provider connectai --prompt-id crm_deals_count --runs 5
  python run_tests.py --provider ipaas --data-source proj_mgmt --runs 3
  python run_tests.py --list-prompts
  python run_tests.py --list-providers
        """
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=list(MCP_PROVIDERS.keys()),
        help="MCP provider to test against"
    )
    parser.add_argument(
        "--data-source",
        type=str,
        choices=list(TEST_PROMPTS.keys()),
        help="Data source to test (crm, proj_mgmt, data_warehouse, erp)"
    )
    parser.add_argument(
        "--prompt-id",
        type=str,
        help="Specific prompt ID to test"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs per test (default: 1)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for results (CSV or JSON based on extension)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5",
        help="LLM model to use (default: gpt-5)"
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List all available test prompts"
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List all available MCP providers"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    # Handle list commands
    if args.list_prompts:
        print("\nAvailable test prompts:")
        print("=" * 80)
        for data_source, prompts in TEST_PROMPTS.items():
            print(f"\n{data_source.upper()}:")
            for p in prompts:
                print(f"  {p['id']}")
                print(f"    {p['prompt'][:70]}...")
                print(f"    Providers: {', '.join(p['providers'])}")
        return

    if args.list_providers:
        print("\nAvailable MCP providers:")
        print("=" * 80)
        for provider, info in MCP_PROVIDERS.items():
            print(f"\n{provider}:")
            print(f"  Name: {info['name']}")
            print(f"  Supports: {', '.join(info['supports'])}")
        return

    # Validate arguments
    if not args.provider:
        print("Error: --provider is required")
        print("Use --list-providers to see available providers")
        sys.exit(1)

    # Get prompts to run
    prompts = []
    if args.prompt_id:
        prompt = get_prompt_by_id(args.prompt_id)
        if not prompt:
            print(f"Error: Unknown prompt ID: {args.prompt_id}")
            print("Use --list-prompts to see available prompts")
            sys.exit(1)
        prompts = [prompt]
    elif args.data_source:
        source_prompts = get_prompts_for_data_source(args.data_source)
        # Filter to prompts that support this provider
        prompts = [
            {**p, "data_source": args.data_source}
            for p in source_prompts
            if args.provider in p["providers"]
        ]
        if not prompts:
            print(f"Error: No prompts for {args.data_source} support provider {args.provider}")
            sys.exit(1)
    else:
        # Get all prompts for this provider
        prompts = get_prompts_for_provider(args.provider)
        if not prompts:
            print(f"Error: No prompts available for provider {args.provider}")
            sys.exit(1)

    # Run tests
    print(f"\n{'='*80}")
    print(f"MCP ACCURACY TEST RUN")
    print(f"{'='*80}")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model}")
    print(f"Prompts to test: {len(prompts)}")
    print(f"Runs per prompt: {args.runs}")
    print(f"Total test runs: {len(prompts) * args.runs}")
    print(f"{'='*80}")

    runner = TestRunner(model=args.model)
    await runner.run_test_suite(
        provider=args.provider,
        prompts=prompts,
        runs_per_test=args.runs,
        verbose=not args.quiet,
    )

    # Print summary
    runner.print_summary()

    # Export results if requested
    if args.output:
        if args.output.endswith('.json'):
            runner.export_results_json(args.output)
        else:
            runner.export_results_csv(args.output)


if __name__ == "__main__":
    asyncio.run(main())
