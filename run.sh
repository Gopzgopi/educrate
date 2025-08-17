#!/bin/bash

# EduCrate - Complete Installation and Run Script
# This script sets up and runs the entire EduCrate platform locally

echo "🎓 EduCrate - Intelligent Educational Platform"
echo "=============================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check port availability
check_port() {
    lsof -ti:$1 >/dev/null 2>&1
}

echo ""
echo "📋 Checking Prerequisites..."

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js found: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js v16+ from https://nodejs.org/"
    exit 1
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
elif command_exists python; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python found: $PYTHON_VERSION"
else
    echo "❌ Python not found. Please install Python 3.8+ from https://python.org/"
    exit 1
fi

# Check yarn
if command_exists yarn; then
    YARN_VERSION=$(yarn --version)
    echo "✅ Yarn found: $YARN_VERSION"
else
    echo "⚠️  Yarn not found. Installing yarn..."
    npm install -g yarn
fi

# Check MongoDB
if command_exists mongod; then
    echo "✅ MongoDB found"
    MONGODB_INSTALLED=true
elif command_exists docker; then
    echo "⚠️  MongoDB not found, but Docker is available"
    echo "   Will use Docker container for MongoDB"
    MONGODB_INSTALLED=false
    DOCKER_AVAILABLE=true
else
    echo "❌ MongoDB not found and Docker not available"
    echo "   Please install MongoDB from https://mongodb.com/try/download/community"
    echo "   Or install Docker from https://docker.com/get-started"
    exit 1
fi

echo ""
echo "🔧 Setting up EduCrate..."

# Create directory structure if needed
mkdir -p /app/backend
mkdir -p /app/frontend

# Setup backend
echo "📦 Installing backend dependencies..."
cd /app/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python requirements
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    echo "MONGO_URL=mongodb://localhost:27017" > .env
fi

echo "✅ Backend setup complete"

# Setup frontend
echo "📦 Installing frontend dependencies..."
cd /app/frontend

# Install Node.js dependencies
yarn install

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
fi

echo "✅ Frontend setup complete"

echo ""
echo "🗄️  Starting Database..."

# Start MongoDB
if [ "$MONGODB_INSTALLED" = true ]; then
    # Check if MongoDB is already running
    if check_port 27017; then
        echo "✅ MongoDB is already running on port 27017"
    else
        echo "Starting MongoDB..."
        # Try to start MongoDB as a service
        if command_exists systemctl; then
            sudo systemctl start mongod 2>/dev/null || true
        elif command_exists brew; then
            brew services start mongodb/brew/mongodb-community 2>/dev/null || true
        else
            # Start MongoDB directly
            mongod --dbpath /tmp/mongodb-data --logpath /tmp/mongodb.log --fork 2>/dev/null || {
                mkdir -p /tmp/mongodb-data
                mongod --dbpath /tmp/mongodb-data --logpath /tmp/mongodb.log --fork
            }
        fi
        
        # Wait for MongoDB to start
        for i in {1..10}; do
            if check_port 27017; then
                echo "✅ MongoDB started successfully"
                break
            fi
            echo "Waiting for MongoDB to start... ($i/10)"
            sleep 2
        done
        
        if ! check_port 27017; then
            echo "⚠️  Could not start MongoDB service, trying Docker..."
            DOCKER_AVAILABLE=true
            MONGODB_INSTALLED=false
        fi
    fi
fi

# Use Docker if needed
if [ "$DOCKER_AVAILABLE" = true ] && [ "$MONGODB_INSTALLED" = false ]; then
    echo "🐳 Starting MongoDB with Docker..."
    
    # Check if container already exists and is running
    if docker ps | grep -q "educrate-mongo"; then
        echo "✅ MongoDB container is already running"
    elif docker ps -a | grep -q "educrate-mongo"; then
        echo "Starting existing MongoDB container..."
        docker start educrate-mongo
    else
        echo "Creating new MongoDB container..."
        docker run -d \
            --name educrate-mongo \
            -p 27017:27017 \
            -v educrate-mongo-data:/data/db \
            mongo:latest
    fi
    
    # Wait for container to be ready
    for i in {1..15}; do
        if docker exec educrate-mongo mongo --eval "db.runCommand('ping')" >/dev/null 2>&1; then
            echo "✅ MongoDB container is ready"
            break
        fi
        echo "Waiting for MongoDB container... ($i/15)"
        sleep 2
    done
fi

echo ""
echo "🚀 Starting EduCrate Services..."

# Function to start backend
start_backend() {
    echo "Starting FastAPI backend on port 8001..."
    cd /app/backend
    source venv/bin/activate
    python server.py &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "Starting React frontend on port 3000..."
    cd /app/frontend
    BROWSER=none yarn start &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
}

# Kill any existing processes on the ports
if check_port 8001; then
    echo "Stopping existing backend process on port 8001..."
    kill $(lsof -ti:8001) 2>/dev/null || true
    sleep 2
fi

if check_port 3000; then
    echo "Stopping existing frontend process on port 3000..."
    kill $(lsof -ti:3000) 2>/dev/null || true
    sleep 2
fi

# Start services
start_backend
sleep 5
start_frontend

# Wait for services to start
echo ""
echo "⏳ Waiting for services to start..."

# Check backend
for i in {1..30}; do
    if curl -s http://localhost:8001/ >/dev/null 2>&1; then
        echo "✅ Backend is ready at http://localhost:8001"
        break
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 2
done

# Check frontend  
for i in {1..30}; do
    if curl -s http://localhost:3000/ >/dev/null 2>&1; then
        echo "✅ Frontend is ready at http://localhost:3000"
        break
    fi
    echo "Waiting for frontend... ($i/30)"
    sleep 2
done

echo ""
echo "🧪 Running API Tests..."
cd /app
python backend_test.py

echo ""
echo "🎉 EduCrate is now running!"
echo "=============================================="
echo ""
echo "📍 Access Points:"
echo "   🌐 Frontend:    http://localhost:3000"
echo "   ⚡ Backend API: http://localhost:8001"
echo "   📚 API Docs:    http://localhost:8001/docs"
echo ""
echo "🔧 Service Management:"
echo "   Backend PID:    $BACKEND_PID"
echo "   Frontend PID:   $FRONTEND_PID"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📖 Next Steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Create your user account"
echo "   3. Complete the learning style assessment"
echo "   4. Create your first AI-powered learning kit!"
echo ""
echo "💡 Features to try:"
echo "   • User registration and learning assessment"
echo "   • Create learning kits with real-time AI processing logs"
echo "   • View generated summaries, flashcards, and audio scripts"
echo "   • Start mood-based study sessions"
echo "   • Ask questions about your learning content"
echo ""
echo "🎓 Happy Learning with EduCrate! ✨"

# Keep script running and monitor services
cleanup() {
    echo ""
    echo "🛑 Shutting down EduCrate services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    
    # Stop Docker container if we started it
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$MONGODB_INSTALLED" = false ]; then
        echo "Stopping MongoDB container..."
        docker stop educrate-mongo 2>/dev/null || true
    fi
    
    echo "✅ All services stopped. Goodbye!"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

echo "Press Ctrl+C to stop all services..."

# Monitor services
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "⚠️  Backend process died, restarting..."
        start_backend
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚠️  Frontend process died, restarting..."
        start_frontend
    fi
    
    sleep 10
done