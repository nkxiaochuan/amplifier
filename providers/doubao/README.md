# Doubao Provider Module

Doubao provider module for Amplifier AI platform.

## Installation

```bash
# Install via git
amplifier module add git+https://github.com/microsoft/amplifier.git#subdirectory=providers/doubao

# Or install from local directory
amplifier module add ./providers/doubao
```

## Configuration

```bash
# Configure Doubao provider
amplifier provider use doubao

# Set API key
# The CLI will prompt you for your Doubao API key
```

## Available Models

- doubao-1.5-pro-128k
- doubao-1.5-pro-256k
- doubao-1.5-mini-128k
- doubao-1.5-flash-128k
- doubao-1.5-flash-256k

## Environment Variables

- `DOUBAO_API_KEY`: Doubao API key (required)
- `DOUBAO_BASE_URL`: Doubao API base URL (optional, default: https://ark.cn-beijing.volces.com/api/v3)

## Usage

```bash
# Use Doubao for a single command
amplifier run --provider doubao "Explain quantum computing"

# Set Doubao as default provider
amplifier provider use doubao
```
