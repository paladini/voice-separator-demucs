#!/bin/bash

# Voice Separator Desktop - Development Script
# This script helps start the desktop application in development mode

set -e

echo "🎵 Voice Separator - Desktop Development Setup"
echo "=" * 50

# Check if we're in the right directory
if [ ! -f "desktop_app.py" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
else
    echo "✅ Python 3 found"
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed"
    exit 1
else
    echo "✅ Node.js found"
fi

if ! command_exists cargo; then
    echo "❌ Rust/Cargo is not installed"
    echo "Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
else
    echo "✅ Rust/Cargo found"
fi

# Install npm dependencies if needed
echo "📦 Checking npm dependencies..."
cd desktop
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
else
    echo "✅ npm dependencies already installed"
fi
cd ..

# Start the Python backend in background
echo "🚀 Starting Python backend..."
python3 desktop_app.py &
PYTHON_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Wait a moment for the backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:7860/health > /dev/null; then
    echo "✅ Backend is running on http://127.0.0.1:7860"
else
    echo "⚠️  Backend might not be ready yet, but continuing..."
fi

# Start Tauri in development mode
echo "🖥️  Starting Tauri desktop application..."
cd desktop
npm run dev

# The script will keep running until Ctrl+C is pressed
# The cleanup function will handle stopping the Python backend
