#!/bin/bash

# Install pnpm globally
npm install -g pnpm

# Install Python development tools
pip install --upgrade pip
pip install black flake8 pytest

# Create virtual environment for backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
pnpm install
cd ..

echo "Devcontainer setup complete!"
echo "Backend virtual environment created at backend/venv"
echo "Frontend dependencies installed"
echo "You can now run:"
echo "  - Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "  - Frontend: cd frontend && pnpm dev"
