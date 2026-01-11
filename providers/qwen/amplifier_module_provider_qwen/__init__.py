"""Qwen provider module for Amplifier."""

import json
import os
from typing import Any, Dict, List, Optional, cast

from amplifier_core.interfaces import Provider
from amplifier_core.message_models import ChatRequest, ChatResponse
from amplifier_core.models import ProviderInfo, ModelInfo, ToolCall

import httpx


class QwenProvider(Provider):
    """Qwen provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Qwen provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.api_key = self._get_api_key()
        self.base_url = config.get("base_url", "https://api.tongyi.ai/v1")
        self.default_model = config.get("default_model", "qwen2.5-7b-instruct")
        self.name = "qwen"

    def _get_api_key(self) -> str:
        """Get Qwen API key from config or environment.

        Returns:
            Qwen API key

        Raises:
            ValueError: If API key is not found
        """
        api_key = self.config.get("api_key")
        if api_key:
            return api_key
        api_key = os.environ.get("QWEN_API_KEY")
        if api_key:
            return api_key
        raise ValueError("Qwen API key not found in config or environment variable QWEN_API_KEY")

    @property
    def name(self) -> str:
        """Provider name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set provider name."""
        self._name = value

    def get_info(self) -> ProviderInfo:
        """Get provider metadata.

        Returns:
            ProviderInfo with id, display_name, credential_env_vars, capabilities, defaults
        """
        return ProviderInfo(
            id="qwen",
            display_name="Qwen",
            credential_env_vars=["QWEN_API_KEY"],
            capabilities=["chat", "completion", "tool_calls"],
            defaults={
                "base_url": "https://api.tongyi.ai/v1",
                "default_model": "qwen2.5-7b-instruct",
            },
            config_fields=[
                {
                    "id": "api_key",
                    "field_type": "secret",
                    "prompt": "Qwen API key",
                    "display_name": "API Key",
                    "env_var": "QWEN_API_KEY",
                    "required": True,
                },
                {
                    "id": "base_url",
                    "field_type": "text",
                    "prompt": "Qwen API base URL",
                    "display_name": "Base URL",
                    "default": "https://api.tongyi.ai/v1",
                    "required": False,
                },
            ],
        )

    async def list_models(self) -> List[ModelInfo]:
        """List available models for this provider.

        Returns:
            List of ModelInfo for available models
        """
        models = [
            ModelInfo(
                id="qwen2.5-72b-instruct",
                display_name="Qwen 2.5 72B Instruct",
                context_window=256000,
                max_output_tokens=4096,
                capabilities=["chat", "completion", "tool_calls"],
            ),
            ModelInfo(
                id="qwen2.5-32b-instruct",
                display_name="Qwen 2.5 32B Instruct",
                context_window=256000,
                max_output_tokens=4096,
                capabilities=["chat", "completion", "tool_calls"],
            ),
            ModelInfo(
                id="qwen2.5-14b-instruct",
                display_name="Qwen 2.5 14B Instruct",
                context_window=256000,
                max_output_tokens=4096,
                capabilities=["chat", "completion", "tool_calls"],
            ),
            ModelInfo(
                id="qwen2.5-7b-instruct",
                display_name="Qwen 2.5 7B Instruct",
                context_window=256000,
                max_output_tokens=4096,
                capabilities=["chat", "completion", "tool_calls"],
            ),
            ModelInfo(
                id="qwen2.5-3b-instruct",
                display_name="Qwen 2.5 3B Instruct",
                context_window=256000,
                max_output_tokens=4096,
                capabilities=["chat", "completion"],
            ),
            ModelInfo(
                id="qwen2.5-1.5b-instruct",
                display_name="Qwen 2.5 1.5B Instruct",
                context_window=256000,
                max_output_tokens=4096,
                capabilities=["chat", "completion"],
            ),
        ]
        return models

    async def complete(self, request: ChatRequest, **kwargs) -> ChatResponse:
        """Generate completion from ChatRequest.

        Args:
            request: Typed chat request with messages, tools, config
            **kwargs: Provider-specific options (override request fields)

        Returns:
            ChatResponse with content blocks, tool calls, usage
        """
        model = kwargs.get("model", request.model or self.default_model)
        messages = request.messages
        tools = request.tools
        temperature = kwargs.get("temperature", request.temperature)
        max_tokens = kwargs.get("max_tokens", request.max_tokens)

        # Convert messages to Qwen format
        qwen_messages = []
        for msg in messages:
            role = msg.role
            content = msg.content
            qwen_messages.append({"role": role, "content": content})

        # Convert tools to Qwen format
        qwen_tools = None
        if tools:
            qwen_tools = []
            for tool in tools:
                qwen_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
                qwen_tools.append(qwen_tool)

        # Build request payload
        payload = {
            "model": model,
            "messages": qwen_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if qwen_tools:
            payload["tools"] = qwen_tools

        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0,
            )

        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Qwen API error: {response.status_code} - {response.text}")

        # Parse response
        response_data = response.json()
        choices = response_data.get("choices", [])
        if not choices:
            raise Exception("Qwen API returned no choices")

        # Convert to ChatResponse
        choice = choices[0]
        message = choice.get("message", {})
        role = message.get("role", "assistant")
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        # Convert tool calls to ToolCall objects
        tool_calls_list = []
        for tool_call in tool_calls:
            tool_call_id = tool_call.get("id")
            tool_call_type = tool_call.get("type")
            function = tool_call.get("function", {})
            function_name = function.get("name")
            function_args = function.get("arguments", "{}")
            
            # Parse arguments
            try:
                args = json.loads(function_args)
            except json.JSONDecodeError:
                args = {}

            tool_call_obj = ToolCall(
                id=tool_call_id,
                type=tool_call_type,
                function={
                    "name": function_name,
                    "arguments": args,
                },
            )
            tool_calls_list.append(tool_call_obj)

        # Build ChatResponse
        chat_response = ChatResponse(
            id=response_data.get("id", ""),
            model=model,
            role=role,
            content=content,
            tool_calls=tool_calls_list,
            usage=response_data.get("usage", {}),
        )

        return chat_response

    def parse_tool_calls(self, response: ChatResponse) -> List[ToolCall]:
        """Parse tool calls from ChatResponse.

        Args:
            response: Typed chat response

        Returns:
            List of tool calls to execute
        """
        return response.tool_calls


# Module export
module = {
    "type": "provider",
    "id": "provider-qwen",
    "name": "Qwen",
    "description": "Qwen provider for Amplifier",
    "implementation": QwenProvider,
}
