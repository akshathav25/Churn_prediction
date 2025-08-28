.PHONY: help setup-backend setup-frontend install run-backend run-frontend dev clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup-backend: ## Set up the Python backend environment
	@echo "Setting up backend..."
	cd backend && python -m venv venv
	cd backend && . venv/bin/activate && pip install -r requirements.txt

setup-frontend: ## Set up the Node.js frontend environment
	@echo "Setting up frontend..."
	cd frontend && pnpm install

install: setup-backend setup-frontend ## Install all dependencies

run-backend: ## Run the FastAPI backend server
	@echo "Starting backend server..."
	cd backend && . venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run the Next.js frontend development server
	@echo "Starting frontend server..."
	cd frontend && pnpm dev

dev: ## Run both backend and frontend in development mode
	@echo "Starting development servers..."
	@make -j2 run-backend run-frontend

clean: ## Clean up generated files and dependencies
	@echo "Cleaning up..."
	rm -rf backend/venv
	rm -rf frontend/node_modules
	rm -rf frontend/.next
	rm -rf frontend/out
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
