#!/bin/bash
# Bento Dashboard Backend Setup Script

echo "🚀 Setting up Dashboard Backend..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data
mkdir -p models

echo "✅ Backend setup complete!"
echo "📖 Next steps:"
echo "   1. Start backend: python main.py"
echo "   2. Open API docs: http://localhost:8000/docs"
