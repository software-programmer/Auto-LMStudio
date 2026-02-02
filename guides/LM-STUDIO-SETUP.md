# LM Studio Setup Guide

This guide explains how to configure Auto Claude to work with LM Studio instead of the default Claude API.

## What is LM Studio?

[LM Studio](https://lmstudio.ai/) is a desktop application that lets you run large language models locally on your machine. This provides:

- **Privacy**: All processing happens locally
- **Cost savings**: No API fees
- **Offline capability**: Works without internet connection
- **Model flexibility**: Use any compatible model

## Prerequisites

1. **LM Studio installed** - Download from [lmstudio.ai](https://lmstudio.ai/)
2. **A compatible model downloaded** - e.g., Llama, Mistral, CodeLlama
3. **Sufficient RAM** - At least 16GB recommended for coding models
4. **Git repository** - Your project must be a git repo

## Setup Steps

### 1. Install and Configure LM Studio

1. Download and install LM Studio for your platform
2. Open LM Studio
3. Download a model suitable for coding (recommendations below)
4. Start the local server:
   - Click the "Local Server" tab
   - Click "Start Server"
   - Note the endpoint (default: `http://127.0.0.1:1234/v1`)

### 2. Configure Auto Claude

#### Option A: Using Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/software-programmer/Auto-LMStudio.git
   cd Auto-LMStudio
   ```

2. Edit `docker-compose.yml` if your LM Studio endpoint is different:
   ```yaml
   environment:
     - ANTHROPIC_BASE_URL=http://192.168.1.85:1234/v1  # Change to your endpoint
     - ANTHROPIC_MODEL=your-model-name  # Change to your model name
   ```

3. Start services:
   ```bash
   docker-compose up -d
   ```

4. Use the CLI:
   ```bash
   docker-compose exec backend python run.py --help
   ```

#### Option B: Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/software-programmer/Auto-LMStudio.git
   cd Auto-LMStudio/apps/backend
   ```

2. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create configuration:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add:
   ```bash
   # LM Studio Configuration
   LLM_PROVIDER=lm_studio
   ANTHROPIC_BASE_URL=http://127.0.0.1:1234/v1
   ANTHROPIC_AUTH_TOKEN=lm-studio
   ANTHROPIC_MODEL=your-model-name
   
   # Disable features that require external APIs
   GRAPHITI_ENABLED=false
   ```

5. Run Auto Claude:
   ```bash
   python run.py --help
   ```

### 3. Find Your Model Name

To find the correct model name to use:

1. Open LM Studio
2. Go to the "Local Server" tab
3. Look for "Model loaded" - this shows the model identifier
4. Use this identifier as your `ANTHROPIC_MODEL` value

Common examples:
- `TheBloke/CodeLlama-13B-Instruct-GGUF`
- `mistralai/Mistral-7B-Instruct-v0.2-GGUF`
- `deepseek-ai/deepseek-coder-6.7b-instruct-GGUF`

## Recommended Models for Coding

| Model | Size | RAM Required | Best For |
|-------|------|-------------|----------|
| **CodeLlama 13B Instruct** | 13B | 16GB+ | General coding, good balance |
| **DeepSeek Coder 33B** | 33B | 32GB+ | Advanced coding, best quality |
| **WizardCoder 15B** | 15B | 20GB+ | Python-focused development |
| **Mistral 7B Instruct** | 7B | 12GB+ | Lightweight, fast responses |
| **Phind CodeLlama 34B** | 34B | 32GB+ | Code completion and reasoning |

## Network Configuration

### Local Machine (localhost)
If Auto Claude and LM Studio are on the same machine:
```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:1234/v1
```

### Different Machine (LAN)
If LM Studio is on a different machine (e.g., `192.168.1.85`):

1. In LM Studio, ensure "Listen on all network interfaces" is enabled
2. Use the LAN IP:
   ```bash
   ANTHROPIC_BASE_URL=http://192.168.1.85:1234/v1
   ```

### Custom Port
If you changed LM Studio's port:
```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:YOUR_PORT/v1
```

## Usage Examples

### Create a Spec
```bash
python spec_runner.py --interactive
```

### Run a Build
```bash
python run.py --spec 001
```

### Run with Quality Assurance
```bash
python run.py --spec 001 --qa
```

### List All Specs
```bash
python run.py --list
```

## Troubleshooting

### "Connection refused" error
- **Cause**: LM Studio server not running
- **Fix**: Start the LM Studio local server

### "Model not found" error
- **Cause**: Incorrect model name in configuration
- **Fix**: Check the model name in LM Studio's "Local Server" tab

### Slow responses
- **Cause**: Model too large for your hardware
- **Fix**: Use a smaller model (7B or 13B instead of 30B+)

### "Out of memory" error
- **Cause**: Model too large for available RAM
- **Fix**: 
  - Close other applications
  - Use a smaller quantization (Q4 instead of Q8)
  - Switch to a smaller model

### Rate limiting issues
- LM Studio doesn't have rate limits
- If you see rate limit errors, you may be accidentally using Claude API
- Verify `LLM_PROVIDER=lm_studio` is set

## Limitations

When using LM Studio instead of Claude:

1. **Extended thinking disabled**: LM Studio models don't support Claude's extended thinking feature
2. **Quality differences**: Open-source models may not match Claude's quality for complex tasks
3. **Tool calling support**: Varies by model (CodeLlama and WizardCoder support it well)
4. **Memory integration**: Graphiti memory features should be disabled or configured separately

## Performance Tips

1. **Use quantized models**: Q4 or Q5 quantization balances quality and speed
2. **GPU acceleration**: Enable GPU in LM Studio settings for faster inference
3. **Adjust context length**: Larger context uses more RAM but handles bigger tasks
4. **Batch processing**: Run multiple small specs instead of one large spec

## Switching Back to Claude

To switch back to Claude API:

1. Edit `.env`:
   ```bash
   LLM_PROVIDER=claude
   # Comment out or remove:
   # ANTHROPIC_BASE_URL=...
   # ANTHROPIC_MODEL=...
   ```

2. Or remove the environment variable:
   ```bash
   unset LLM_PROVIDER
   ```

3. Restart Auto Claude

## Further Reading

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [OpenAI-Compatible API Reference](https://platform.openai.com/docs/api-reference)
- [Model Quantization Guide](https://huggingface.co/docs/transformers/main/en/quantization)

## Support

For LM Studio-specific issues:
- LM Studio Discord: Check their official website
- GitHub Issues: Report bugs specific to Auto Claude + LM Studio integration

For Auto Claude issues:
- [GitHub Issues](https://github.com/software-programmer/Auto-LMStudio/issues)
- [Discord Community](https://discord.gg/KCXaPBr4Dj)
