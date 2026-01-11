# DeepSeek Provider Module

DeepSeek provider module for Amplifier AI platform.

## Installation

```bash
# Install via git
amplifier module add git+https://github.com/microsoft/amplifier.git#subdirectory=providers/deepseek

# Or install from local directory
amplifier module add ./providers/deepseek
```

## Configuration

```bash
# Configure DeepSeek provider
amplifier provider use deepseek

# Set API key
# The CLI will prompt you for your DeepSeek API key
```

## Available Models

- deepseek-chat
- deepseek-llm
- deepseek-coder
- deepseek-visual
- deepseek-r1

## Environment Variables

- `DEEPSEEK_API_KEY`: DeepSeek API key (required)
- `DEEPSEEK_BASE_URL`: DeepSeek API base URL (optional, default: https://api.deepseek.com/v1)

## Usage

```bash
# Use DeepSeek for a single command
amplifier run --provider deepseek "Explain quantum computing"

# Set DeepSeek as default provider
amplifier provider use deepseek
```
