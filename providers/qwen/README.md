# Qwen Provider Module

Qwen provider module for Amplifier AI platform.

## Installation

```bash
# Install via git
amplifier module add git+https://github.com/microsoft/amplifier.git#subdirectory=providers/qwen

# Or install from local directory
amplifier module add ./providers/qwen
```

## Configuration

```bash
# Configure Qwen provider
amplifier provider use qwen

# Set API key
# The CLI will prompt you for your Qwen API key
```

## Available Models

- qwen2.5-72b-instruct
- qwen2.5-32b-instruct
- qwen2.5-14b-instruct
- qwen2.5-7b-instruct
- qwen2.5-3b-instruct
- qwen2.5-1.5b-instruct

## Environment Variables

- `QWEN_API_KEY`: Qwen API key (required)
- `QWEN_BASE_URL`: Qwen API base URL (optional, default: https://api.tongyi.ai/v1)

## Usage

```bash
# Use Qwen for a single command
amplifier run --provider qwen "Explain quantum computing"

# Set Qwen as default provider
amplifier provider use qwen
```
