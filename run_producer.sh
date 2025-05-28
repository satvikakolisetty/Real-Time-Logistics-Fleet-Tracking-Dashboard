#!/bin/bash

echo "Starting GPS Data Producer"
echo "========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python3 -c "import faker, kafka" 2>/dev/null; then
    echo "Dependencies not installed. Installing now..."
    pip3 install -r requirements.txt
fi

# Check if Docker services are running
if ! docker ps | grep -q "kafka"; then
    echo "Docker services not running. Please start services first:"
    echo "   docker compose up -d"
    exit 1
fi

echo "All checks passed. Starting producer..."
echo "Press Ctrl+C to stop the producer"
echo ""

# Run the producer
python3 producer/producer.py 