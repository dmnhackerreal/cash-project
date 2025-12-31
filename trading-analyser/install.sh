#!/bin/bash

# Trading Analysis Tool - Installation Script

echo "🚀 Installing Trading Analysis Tool..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install TA-Lib dependencies (Linux/macOS)
echo "📊 Installing TA-Lib dependencies..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo apt-get update
    sudo apt-get install -y build-essential
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib/
    ./configure --prefix=/usr
    make
    sudo make install
    cd ..
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew install ta-lib
    
elif [[ "$OSTYPE" == "msys" ]]; then
    # Windows (Git Bash)
    echo "⚠️ Windows users: Please install TA-Lib manually from:"
    echo "https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib"
    echo "Then run: pip install TA_Lib‑0.4.28‑cp3xx‑cp3xx‑win_amd64.whl"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs reports cache

# Copy environment file
echo "⚙️ Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x main.py
chmod +x examples/*.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run the tool:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run main script: python main.py"
echo "3. Or run examples: python examples/basic_usage.py"
echo ""
echo "Don't forget to add your API keys to the .env file!"
