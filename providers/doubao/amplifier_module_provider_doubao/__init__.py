"""Doubao provider module for Amplifier."""

import json
import os
from typing import Any, Dict, List, Optional, cast

from amplifier_core.interfaces import Provider
from amplifier_core.message_models import ChatRequest, ChatResponse
from amplifier_core.models import ProviderInfo, ModelInfo, ToolCall

import httpx


class DoubaoProvider(Provider):
    """Doubao provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Doubao provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.api_key = self._get_api_key()
        self.base_url = config.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
        self.default_model = config.get("default_model", "doubao-1.5-pro-128k")
        self.name = "doubao"

    def _get_api_key(self) -> str:
        """Get Doubao API key from config or environment.

        Returns:
            Doubao API key

        Raises:
            ValueError: If API key is not found
        """
        api_key = self.config.get("api_key")
        if api_key:
            return api_key
        api_key = os.environ.get("DOUBAO_API_KEY")
        if api_key:
            return api_key
        raise ValueError("Doubao API key not found in config or environment variable DOUBAO_API_KEY")

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
            id="doubao",
            display_name="Doubao",
            credential_env_vars=["DOUBAO_API_KEY"],
            capabilities=["chat", "completion", "tool_calls"],
            defaults={
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "default_model": "doubao-1.5-pro-128k",
            },
            config_fields=[
                {
                    "id": "api_key",
                    "field_type": "secret",
                    "prompt": "Doubao API key",
                    "display_name": "API Key",
                    "env_var": "DOUBAO_API_KEY",
                    "required": True,
                },
                {
                    "id": "base_url",
                    "field_type": "text",
                    "prompt": "Doubao API base URL",
                    "display_name": "Base URL",
                    "default": "https://ark.cn-beijing.volces.com/api/v3",
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
                id="doubao-1.5-pro-128k",
                display_name="Doubao 1.5 Pro 128k",
                context_window=128000,
                max_output_tokens=4096,
                capabilities=["chat", "completion", "tool_calls"],
            ),
            ModelInfo(
                id="doubao-1.5-pro-256k",
                display_name="Doubao 1.5 Pro 256k",
                context_window=256000,
                max_output_tokens=4096,
                capabilities=["chat", "completion", "tool_calls"],
            ),
            ModelInfo(
                id="doubao-1.5-mini-128k",
                display_name="Doubao 1.5 Mini 128k",
                context_window=128000,
                max_output_tokens=4096,
                capabilities=["chat", "completion"],
            ),
            ModelInfo(
                id="doubao-1.5-flash-128k",
                display_name="Doubao 1.5 Flash 128k",
                context_window=128000,
                max_output_tokens=4096,
                capabilities=["chat", "completion"],
            ),
            ModelInfo(
                id="doubao-1.5-flash-256k",
                display_name="Doubao 1.5 Flash 256k",
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

        # Convert messages to Doubao format
        doubao_messages = []
        for msg in messages:
            role = msg.role
            content = msg.content
            doubao_messages.append({"role": role, "content": content})

        # Convert tools to Doubao format
        doubao_tools = None
        if tools:
            doubao_tools = []
            for tool in tools:
                doubao_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
                doubao_tools.append(doubao_tool)

        # Build request payload
        payload = {
            "model": model,
            "messages": doubao_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if doubao_tools:
            payload["tools"] = doubao_tools

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
            raise Exception(f"Doubao API error: {response.status_code} - {response.text}")

        # Parse response
        response_data = response.json()
        choices = response_data.get("choices", [])
        if not choices:
            raise Exception("Doubao API returned no choices")

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
    "id": "provider-doubao",
    "name": "Doubao",
    "description": "Doubao provider for Amplifier",
    "implementation": DoubaoProvider,
}
