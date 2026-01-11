# 国内模型提供商集成指南

## 已实现的提供商

1. **DeepSeek** - 深度求索模型
2. **Doubao** - 豆包模型
3. **Qwen** - 通义千问模型

## 安装方法

### 从本地目录安装

```bash
# 安装DeepSeek提供商
amplifier module add ./providers/deepseek

# 安装Doubao提供商
amplifier module add ./providers/doubao

# 安装Qwen提供商
amplifier module add ./providers/qwen
```

### 从Git仓库安装

```bash
# 安装DeepSeek提供商
amplifier module add git+https://github.com/microsoft/amplifier.git#subdirectory=providers/deepseek

# 安装Doubao提供商
amplifier module add git+https://github.com/microsoft/amplifier.git#subdirectory=providers/doubao

# 安装Qwen提供商
amplifier module add git+https://github.com/microsoft/amplifier.git#subdirectory=providers/qwen
```

## 配置方法

```bash
# 配置DeepSeek提供商
amplifier provider use deepseek

# 配置Doubao提供商
amplifier provider use doubao

# 配置Qwen提供商
amplifier provider use qwen
```

## 环境变量

- **DeepSeek**: `DEEPSEEK_API_KEY`
- **Doubao**: `DOUBAO_API_KEY`
- **Qwen**: `QWEN_API_KEY`

## 手动更新提供商显示名称列表（可选）

如果需要在CLI中看到正确的显示名称，可以手动更新 `amplifier-app-cli/amplifier_app_cli/provider_manager.py` 文件中的 `_PROVIDER_DISPLAY_NAMES` 字典：

```python
_PROVIDER_DISPLAY_NAMES = {
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "azure-openai": "Azure OpenAI",
    "gemini": "Google Gemini",
    "ollama": "Ollama",
    "vllm": "vLLM",
    "deepseek": "DeepSeek",  # 添加这一行
    "doubao": "Doubao",      # 添加这一行
    "qwen": "Qwen",          # 添加这一行
}
```

## 测试方法

```bash
# 查看可用提供商
amplifier provider list

# 测试DeepSeek
amplifier run --provider deepseek "你好，我是测试用户"

# 测试Doubao
amplifier run --provider doubao "你好，我是测试用户"

# 测试Qwen
amplifier run --provider qwen "你好，我是测试用户"
```

## 支持的模型

### DeepSeek
- deepseek-chat
- deepseek-llm
- deepseek-coder
- deepseek-visual
- deepseek-r1

### Doubao
- doubao-1.5-pro-128k
- doubao-1.5-pro-256k
- doubao-1.5-mini-128k
- doubao-1.5-flash-128k
- doubao-1.5-flash-256k

### Qwen
- qwen2.5-72b-instruct
- qwen2.5-32b-instruct
- qwen2.5-14b-instruct
- qwen2.5-7b-instruct
- qwen2.5-3b-instruct
- qwen2.5-1.5b-instruct
