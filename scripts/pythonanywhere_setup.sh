#!/bin/bash

# PythonAnywhere Setup & Migration Script
# Run this script on your PythonAnywhere console (Bash)

echo "========================================================"
echo "      AZAD SYSTEM - PYTHONANYWHERE DEPLOYMENT TOOL      "
echo "========================================================"

# 1. Configuration
PROJECT_DIR="/home/NASERALLAH/ramallah"
VENV_DIR="/home/NASERALLAH/.virtualenvs/garage_venv"
REPO_URL="https://github.com/AbuAzad2025/AzadAccounting-sys.git"
DB_HOST="NASERALLAH-4986.postgres.pythonanywhere-services.com"
DB_PORT="14986"
DB_USER="super"
DB_NAME="super" # Please verify this on your PA Databases tab

echo "[1/6] Checking Environment..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Project directory not found. Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
else
    echo "Project directory exists. Pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
fi

cd "$PROJECT_DIR"

# 2. Virtual Environment
echo "[2/6] Setting up Virtual Environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtualenv..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 3. Dependencies
echo "[3/6] Installing Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install psycopg2-binary

# 4. Environment Variables
echo "[4/6] Configuring .env file..."
ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo ".env file already exists."
else
    echo "Creating .env file..."
    read -sp "Enter Database Password: " DB_PASSWORD
    echo ""
    
    cat <<EOF > "$ENV_FILE"
APP_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8080
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
SECRET_KEY=$(openssl rand -hex 32)
# Add other settings as needed
EOF
    echo ".env file created."
fi

# 5. Database Migration
echo "[5/6] Migrating Database..."

DUMP_FILE="$PROJECT_DIR/production_data.json.gz"

if [ -f "$DUMP_FILE" ]; then
    echo "Found local data dump: $DUMP_FILE"
    echo "Restoring data to Production Database..."
    python Scripts/db_migration_tool.py restore
else
    echo "WARNING: $DUMP_FILE not found!"
    echo "Please upload 'production_data.json.gz' to '$PROJECT_DIR' and run this script again or run:"
    echo "python Scripts/db_migration_tool.py restore"
fi

# 6. Final Steps
echo "[6/6] Finalizing..."
# Run any other upgrade scripts if needed
# python Scripts/db_upgrade_pipeline.py

echo "========================================================"
echo "DEPLOYMENT COMPLETED!"
echo "Please reload your web app from the PythonAnywhere Dashboard."
echo "========================================================"
