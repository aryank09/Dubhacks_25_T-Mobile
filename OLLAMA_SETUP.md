# Local AI Setup with Ollama

## Why Ollama?

✅ **FREE** - No API costs  
✅ **Offline** - Works without internet  
✅ **Private** - All data stays on your Pi  
✅ **Fast** - Optimized models for Raspberry Pi  
✅ **No API keys needed**

## Installation (Automatic)

The `install.sh` script automatically installs Ollama! Just run:

```bash
./install.sh
```

## Manual Installation (if needed)

### On Raspberry Pi:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Download a model
ollama pull phi  # Recommended for Pi 4 (2.7GB)
# OR
ollama pull tinyllama  # Smallest, fastest (637MB)
```

## Recommended Models for Raspberry Pi

### 1. **Phi** (Recommended) ✨
- **Size**: 2.7GB
- **RAM**: 4GB+ Pi
- **Speed**: ~2-3 seconds per response
- **Quality**: Excellent for navigation tasks
```bash
ollama pull phi
```

### 2. **TinyLlama** (Budget option)
- **Size**: 637MB
- **RAM**: 2GB+ Pi
- **Speed**: ~1-2 seconds per response
- **Quality**: Good for simple tasks
```bash
ollama pull tinyllama
```

### 3. **Llama2:7b** (If you have Pi 5 with 8GB)
- **Size**: 3.8GB
- **RAM**: 8GB Pi
- **Speed**: ~3-4 seconds per response
- **Quality**: Best quality
```bash
ollama pull llama2:7b
```

## Usage

The system is already configured to use Ollama by default!

### Check Status:

```bash
# Check if Ollama is running
ollama list

# Test Ollama
ollama run phi "Hello, how are you?"
```

### In Your Code:

The `.env` file is already set to:
```
AI_SERVICE=ollama
```

No API keys needed! Just run:
```bash
python3 main.py
```

## Switching Models

Edit `ai_brain.py` line 153 to change models:

```python
response = self.client.chat(
    model='phi',  # Change this to 'tinyllama', 'llama2', or 'mistral'
    messages=messages,
```

## Performance on Raspberry Pi

| Model | Pi 4 (4GB) | Pi 4 (8GB) | Pi 5 (8GB) |
|-------|------------|------------|------------|
| tinyllama | ✅ Fast | ✅ Fast | ✅ Very Fast |
| phi | ✅ Good | ✅ Great | ✅ Excellent |
| llama2:7b | ⚠️ Slow | ✅ Good | ✅ Great |

## Troubleshooting

### "Connection refused"
```bash
# Restart Ollama
sudo systemctl restart ollama

# Check status
sudo systemctl status ollama
```

### "Model not found"
```bash
# Download the model
ollama pull phi

# List available models
ollama list
```

### "Out of memory"
Use a smaller model:
```bash
ollama pull tinyllama
# Then edit ai_brain.py to use 'tinyllama'
```

### Slow responses
- Use `tinyllama` for faster responses
- Close other applications
- Reduce `num_predict` in ai_brain.py (line 157)

## Comparing with Cloud AI

| Feature | Ollama (Local) | OpenAI/Gemini |
|---------|----------------|---------------|
| Cost | FREE ✅ | $0.002+ per request |
| Internet | Not needed ✅ | Required |
| Privacy | 100% private ✅ | Data sent to cloud |
| Setup | Easy ✅ | Need API key |
| Speed | 2-4 sec | 1-2 sec |
| Quality | Good | Excellent |

## Best for Hackathon

**Use Ollama with Phi model:**
1. No API costs during demo
2. Works without WiFi
3. Privacy for users
4. Shows technical skill
5. Good enough quality for navigation

## Alternative: Use Both!

You can switch between local and cloud:

```bash
# Use local (free, offline)
export AI_SERVICE=ollama
python3 main.py

# Use cloud (better quality, needs internet)
export AI_SERVICE=gemini  # or openai
python3 main.py
```

Perfect for demos: Start with Ollama, switch to cloud if needed!

