# 🔴 The Red Room: The Infinite Adversary

**Autonomous AI Security Testing System**

[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)]()
[![Scanner](https://img.shields.io/badge/Scanner-Production%20Ready-green)]()
[![Tests](https://img.shields.io/badge/Tests-70-blue)]()

---

## 🎯 What is The Red Room?

An autonomous AI security testing system that uses three specialized agents to find, exploit, and fix vulnerabilities:

1. **Saboteur** (Agent I) - Analyzes code changes and generates attack hypotheses
2. **Exploit Lab** (Agent II) - Executes exploits in isolated shadow environments
3. **Surgeon** (Agent III) - Generates patches and creates pull requests

---

## ⚡ Quick Start

### Installation (5 minutes):
```bash
# Clone repository
git clone https://github.com/yourusername/Red-Room.git
cd Red-Room

# Setup environment
setup-conda-env.bat

# Start scanner
start-realtime-scanner-conda.bat
```

### Access:
Open browser to: **http://127.0.0.1:5000**

### Test:
Enter `http://httpbin.org` and click "Start Scan"

---

## ✨ Features

### 🔍 Web Scanner (Production Ready)
- **70 vulnerability tests** covering OWASP Top 10
- **Real-time progress** with WebSocket updates
- **Scan history** with SQLite database
- **PDF reports** for stakeholders
- **Beautiful UI** with dark theme

### 🤖 Three-Agent System (In Development)
- **NPU-accelerated** hypothesis generation
- **GPU-accelerated** exploit execution
- **Automated** patch generation
- **LangGraph** orchestration

### 🔧 Hardware Support
- **Hardware-agnostic** - works on any laptop
- **AMD optimization** - NPU/GPU acceleration
- **NVIDIA support** - CUDA acceleration
- **Intel support** - CPU fallback

---

## 📊 Current Status

| Component | Status | Completion |
|-----------|--------|------------|
| Web Scanner | ✅ Production Ready | 100% |
| Real-Time Progress | ✅ Complete | 100% |
| Scan History | ✅ Complete | 100% |
| PDF Reports | ✅ Complete | 100% |
| Agent I (Saboteur) | ⏳ In Progress | 40% |
| Agent II (Exploit Lab) | ⏳ In Progress | 20% |
| Agent III (Surgeon) | ⏳ In Progress | 30% |
| Orchestrator | ⏳ In Progress | 10% |

---

## 📚 Documentation

### Essential Reading:
- **[PROJECT-MASTER.md](PROJECT-MASTER.md)** - 📄 **START HERE** - Single source of truth
- **[design.md](design.md)** - Original system design
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation guide

### Guides:
- **[HARDWARE-SUPPORT.md](HARDWARE-SUPPORT.md)** - Hardware acceleration guide
- **[SAFE-TESTING-SITES.md](SAFE-TESTING-SITES.md)** - Legal testing resources
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

---

## 🚀 Usage

### Web Scanner:
```bash
# Start scanner
start-realtime-scanner-conda.bat

# Visit http://127.0.0.1:5000
# Enter target URL
# Click "Start Scan"
# Watch real-time progress
# View results and download PDF
```

### Command Line:
```bash
# Activate environment
conda activate redroom

# Run scan
python -m redroom.cli scan https://example.com

# View history
python -m redroom.cli history

# Generate report
python -m redroom.cli report <scan_id>
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Web Scanner (Working)            │
│  - 70 vulnerability tests                │
│  - Real-time WebSocket updates           │
│  - SQLite database                       │
│  - PDF report generation                 │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│      Three-Agent System (Partial)        │
│                                          │
│  Git Diff → Agent I (Saboteur/NPU)      │
│           → Agent II (Exploit Lab/GPU)   │
│           → Agent III (Surgeon/CPU)      │
│           → Pull Request                 │
└─────────────────────────────────────────┘
```

---

## 🎯 Roadmap

### ✅ Phase 1: Scanner (Complete)
- 70 vulnerability tests
- Real-time progress
- Scan history
- PDF reports

### ⏳ Phase 2: Agent System (In Progress)
- Agent I: Hypothesis generation
- Agent II: Exploit execution
- Agent III: Patch generation
- LangGraph orchestration

### 📅 Phase 3: Production (Planned)
- CI/CD integration
- Scheduled scans
- Team collaboration
- Enterprise features

---

## 🔧 Development

### Setup:
```bash
# Clone and setup
git clone https://github.com/yourusername/Red-Room.git
cd Red-Room
setup-conda-env.bat

# Activate environment
conda activate redroom

# Install dev dependencies
pip install -r requirements-realtime.txt
```

### Run Tests:
```bash
# Test scanner
python test_httpbin.py

# Run all tests
pytest tests/

# Test specific agent
pytest tests/unit/test_saboteur.py
```

### Project Structure:
```
The-Red-Room/
├── src/redroom/
│   ├── agents/          # Three agents + scanner
│   ├── database/        # Scan history
│   ├── reports/         # PDF generation
│   ├── utils/           # Hardware detection
│   └── orchestrator/    # LangGraph
├── templates/           # Web UI
├── web_scanner_app_realtime.py  # Main app
└── PROJECT-MASTER.md   # Documentation
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas Needing Help:
- Agent II (Exploit Lab) implementation
- Agent III (Surgeon) enhancement
- LangGraph orchestrator
- Additional vulnerability tests
- Documentation improvements

---

## ⚠️ Legal Notice

**Only scan websites you own or have permission to test.**

Unauthorized security testing is illegal. Use responsibly.

### Safe Testing Sites:
- http://testphp.vulnweb.com
- http://demo.testfire.net
- http://httpbin.org

See [SAFE-TESTING-SITES.md](SAFE-TESTING-SITES.md) for more.

---

## 📊 Statistics

- **Lines of Code**: ~5,000
- **Vulnerability Tests**: 70
- **OWASP Coverage**: 100%
- **Hardware Support**: CPU/GPU/NPU
- **Database**: SQLite
- **Real-Time**: WebSocket

---

## 📞 Support

### Documentation:
- Read [PROJECT-MASTER.md](PROJECT-MASTER.md) first
- Check [INSTALLATION.md](INSTALLATION.md) for setup issues
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

### Issues:
- Report bugs on GitHub Issues
- Ask questions in Discussions
- Contribute via Pull Requests

---

## 📄 License

[Your License Here]

---

## 🙏 Acknowledgments

Built with:
- Flask & Flask-SocketIO
- SQLite
- ReportLab
- LangGraph
- AMD ROCm / NVIDIA CUDA

---

## 🎯 Next Steps

1. **Read [PROJECT-MASTER.md](PROJECT-MASTER.md)** - Understand the project
2. **Run the scanner** - Test it out
3. **Check the code** - Explore `src/redroom/`
4. **Contribute** - Help build the agent system

---

**🔴 The Red Room: The Infinite Adversary 🛡️**

*Autonomous AI Security Testing*

---

**Quick Links:**
- [Documentation](PROJECT-MASTER.md)
- [Installation](INSTALLATION.md)
- [Architecture](ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
