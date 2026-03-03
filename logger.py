#!/usr/bin/env python3
"""
Shared logging utilities for the LangChain MCP testing harness.
Provides consistent token tracking and cost calculation across all test files.
"""
from langchain_core.callbacks import BaseCallbackHandler


class DynamicToolLogger(BaseCallbackHandler):
    """
    LangChain callback handler for monitoring tool calls and LLM token usage.

    Captures metrics from the OpenAI API response including:
    - Tool call counts
    - Prompt and completion tokens
    - Cost calculations based on GPT-5 pricing
    """

    # GPT-5 API Pricing (per 1M tokens)
    GPT5_INPUT_PRICE = 1.250    # $1.250 per 1M input tokens
    GPT5_OUTPUT_PRICE = 10.000  # $10.000 per 1M output tokens
    GPT5_CACHED_INPUT_PRICE = 0.125  # $0.125 per 1M cached input tokens

    def __init__(self, model_name: str = "gpt-5"):
        super().__init__()
        self.model_name = model_name
        self.tool_call_count = 0

        # OpenAI API token tracking
        self.llm_prompt_tokens = 0
        self.llm_completion_tokens = 0
        self.llm_total_tokens = 0
        self.llm_call_count = 0

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        """Runs when a tool is started."""
        self.tool_call_count += 1
        tool_name = serialized.get('name', 'unknown')

        print("--- Starting tool call ---")
        print(f"Tool name: {tool_name}")
        print(f"Tool call #: {self.tool_call_count}")
        print(f"Tool input: {input_str[:100]}{'...' if len(input_str) > 100 else ''}")
        print("-------------------------")

    def on_tool_end(self, output, **kwargs) -> None:
        """Runs when a tool is ended."""
        output_str = str(output) if output is not None else ""

        print("--- Tool call ended ---")
        print(f"Tool output: {output_str[:200]}{'...' if len(output_str) > 200 else ''}")
        print("-------------------------")

    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Runs when a tool errors."""
        print("--- Tool call error ---")
        print(f"Error: {error}")
        print("-------------------------")

    def on_llm_end(self, response, **kwargs) -> None:
        """Runs when LLM ends running - tracks actual token usage from OpenAI API."""
        self.llm_call_count += 1

        # Extract actual token usage from OpenAI API response
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', 0)

            self.llm_prompt_tokens += prompt_tokens
            self.llm_completion_tokens += completion_tokens
            self.llm_total_tokens += total_tokens

        # Print token usage for this call
        print("=" * 70)
        print(f"LLM Call #{self.llm_call_count} - Token Usage")
        print("=" * 70)
        print(f"Prompt tokens:     {prompt_tokens:>6}")
        print(f"Completion tokens: {completion_tokens:>6}")
        print(f"Total tokens:      {total_tokens:>6}")
        print("-" * 70)
        print(f"Cumulative prompt tokens:     {self.llm_prompt_tokens:>6}")
        print(f"Cumulative completion tokens: {self.llm_completion_tokens:>6}")
        print(f"Cumulative total tokens:      {self.llm_total_tokens:>6}")
        print("=" * 70)

    def get_summary(self) -> dict:
        """Get summary of tool call and LLM token usage statistics."""
        # Calculate costs based on actual API token counts
        input_cost = (self.llm_prompt_tokens / 1_000_000) * self.GPT5_INPUT_PRICE
        output_cost = (self.llm_completion_tokens / 1_000_000) * self.GPT5_OUTPUT_PRICE
        total_cost = input_cost + output_cost

        return {
            # Tool statistics
            "total_tool_calls": self.tool_call_count,

            # LLM statistics (from OpenAI API)
            "llm_calls": self.llm_call_count,
            "llm_prompt_tokens": self.llm_prompt_tokens,
            "llm_completion_tokens": self.llm_completion_tokens,
            "llm_total_tokens": self.llm_total_tokens,
            "average_llm_tokens_per_call": self.llm_total_tokens / max(self.llm_call_count, 1),

            # Cost calculations (based on actual API token counts)
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        }

    def print_final_summary(self) -> None:
        """Print a formatted summary of all collected metrics."""
        summary = self.get_summary()

        print("\n" + "=" * 80)
        print("📊 FINAL TOKEN USAGE STATISTICS")
        print("=" * 80)

        # Tool statistics
        print("\n🔧 TOOL CALL STATISTICS:")
        print(f"   Total tool calls: {summary['total_tool_calls']}")

        # LLM statistics (actual from API)
        print("\n🤖 LLM TOKEN USAGE (from OpenAI API):")
        print("-" * 80)
        print(f"Number of LLM calls: {summary['llm_calls']}")
        print(f"Prompt tokens:     {summary['llm_prompt_tokens']:>8,}")
        print(f"Completion tokens: {summary['llm_completion_tokens']:>8,}")
        print(f"Total LLM tokens:  {summary['llm_total_tokens']:>8,}")
        print(f"Average tokens per LLM call: {summary['average_llm_tokens_per_call']:.1f}")

        # Cost calculations (based on actual API counts)
        print("\n💰 COST BREAKDOWN (GPT-5 Pricing: $1.25/1M input, $10.00/1M output):")
        print("-" * 80)
        print(f"Input cost:  ${summary['input_cost']:.4f}")
        print(f"Output cost: ${summary['output_cost']:.4f}")
        print(f"Total cost:  ${summary['total_cost']:.4f}")

        print("=" * 80)
