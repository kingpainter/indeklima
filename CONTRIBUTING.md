# Contributing to Indeklima 🏠

Thank you for considering contributing to Indeklima! 🎉

## 🚀 Quick Start

1. **Fork** the project on GitHub
2. **Clone** your fork: `git clone https://github.com/YOUR-USERNAME/indeklima.git`
3. **Create a branch**: `git checkout -b feature/my-feature`
4. **Make your changes**
5. **Test** in Home Assistant
6. **Commit**: `git commit -m 'Add my feature'`
7. **Push**: `git push origin feature/my-feature`
8. **Open a Pull Request** on GitHub

## 💻 Development Setup

### Requirements
- Home Assistant 2024.1.0+
- Python 3.11+
- A test Home Assistant installation

### Local Development
1. Copy `custom_components/indeklima` to your HA `custom_components/` folder
2. Restart Home Assistant
3. Add integration via UI: Settings → Integrations → Add → Indeklima
4. Make changes and restart HA to test

### Test Environment
It's recommended to have a **separate test installation** of Home Assistant so you don't affect your live system.

## 📋 Code Standards

### Python Code
- ✅ **ALL Python code in ENGLISH**
- ❌ **NO Danish characters (æ, ø, å) in Python files**
- ✅ **Type hints always**: `def my_func(param: str) -> bool:`
- ✅ **Docstrings** for functions and classes
- ✅ **Error handling** with try/except

### Comments
- **English preferred**, but Danish OK if it helps understanding
- Explain WHY, not just WHAT

### Formatting
- Follow [Home Assistant's style guide](https://developers.home-assistant.io/docs/development_guidelines/)
- 4 spaces indentation (not tabs)
- Max 88 characters per line (Black formatter standard)

### Example
```python