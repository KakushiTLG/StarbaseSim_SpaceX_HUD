Real-time telemetry interface for StarbaseSim that displays live rocket data including engine status, fuel levels, altitude, speed, and vehicle attitude indicators.

For fun because why not? https://youtu.be/cQhGCeIEZfY

Pictures of booster and ship were honestly stolen from @ker_1010 on Discord, from the StarbaseSim Discord server! (I'm sorry!)

## Installation & Quick Start

### Windows (Recommended)

1. **Install Python 3.7+** from https://python.org
2. **Run the installer**: Double-click `install_and_launch.bat`
3. **Open browser**: Navigate to `http://localhost:5000`

The installer will automatically create a virtual environment, install dependencies, and launch the GUI.

### Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the application
python main.py
```