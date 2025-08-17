# EduCrate - Intelligent Educational Platform

EduCrate is a complete full-stack educational platform that generates personalized learning kits tailored to individual learning styles (visual, auditory, textual, kinesthetic). The platform uses local AI processing to create summaries, flashcards, audio lessons, and visual doodles without requiring any external APIs or paid services.

## 🎯 Features

### Core Functionality
- **User Registration & Authentication**: Complete user management system
- **Learning Style Assessment**: 5-question scientific assessment to determine user's preferred learning styles
- **Personalized Dashboard**: Statistics, recent activity, and navigation hub
- **AI-Powered Content Generation**: Local processing for multiple content types
- **Study Session Management**: Mood-based learning recommendations
- **Real-time QA System**: Context-aware question answering
- **Analytics Dashboard**: Progress tracking and learning insights

### AI Content Generation (100% Local)
- **Smart Summaries**: Style-adapted content summaries
- **Interactive Flashcards**: Automatically generated Q&A pairs with hints
- **Audio Lesson Scripts**: Conversational scripts optimized for listening
- **Visual Doodle Descriptions**: Detailed drawing instructions for visual learners
- **QA Indexing**: Searchable content structure for quick answers

### Learning Style Support
- **Visual**: Diagrams, charts, color-coded content, doodle instructions
- **Auditory**: Audio scripts, discussion formats, verbal explanations  
- **Textual**: Detailed written content, summaries, structured notes
- **Kinesthetic**: Hands-on activities, practical applications, real-world examples

## 🏗️ Technology Stack

### Frontend
- **React 19**: Modern JavaScript framework
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality React component library
- **Lucide React**: Beautiful icon library
- **Axios**: HTTP client for API requests

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: NoSQL database with Motor async driver
- **Pydantic**: Data validation and settings management
- **Python 3.8+**: Core programming language

### Local AI Processing
- **No External APIs Required**: All AI functionality runs locally
- **Intelligent Content Analysis**: Text processing and key concept extraction
- **Style-Adaptive Generation**: Content tailored to learning preferences
- **Real-time Processing Logs**: Visible status updates during generation

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React application
│   │   ├── App.css           # Custom styles
│   │   ├── index.js          # React entry point
│   │   └── components/ui/    # shadcn/ui components
│   ├── package.json          # Node.js dependencies
│   └── public/               # Static assets
├── backend_test.py           # API testing suite
└── README.md                # This file
```

## 🚀 Installation & Setup

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (3.8 or higher) 
- **MongoDB** (local installation or Docker)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd educrate-platform
```

### 2. Backend Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
echo "MONGO_URL=mongodb://localhost:27017" > .env

# Start MongoDB (if using Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or start MongoDB locally
mongod --dbpath /your/mongodb/data/path
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install Node.js dependencies
yarn install

# Set environment variables (create .env file)
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
```

### 4. Run the Application

#### Option A: Manual Start
```bash
# Terminal 1: Start Backend
cd backend
python server.py

# Terminal 2: Start Frontend  
cd frontend
yarn start
```

#### Option B: Using Supervisor (Production-like)
```bash
# Start all services
sudo supervisorctl restart all

# Check service status
sudo supervisorctl status
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🧪 Testing

### Run Backend API Tests
```bash
cd /app
python backend_test.py
```

### Expected Test Results
```
📊 FINAL RESULTS:
   Tests Run: 11
   Tests Passed: 11
   Success Rate: 100.0%
🎉 All tests passed! Backend is working correctly.
```

### Manual Testing Checklist
1. **User Registration**: Create account with name, email, language
2. **Learning Assessment**: Complete 5-question style assessment
3. **Dashboard Access**: View stats and navigate between tabs
4. **Kit Creation**: Generate learning kit with real-time logs
5. **Content Viewing**: Browse generated summaries, flashcards, etc.
6. **Study Sessions**: Start mood-based study recommendations

## 🎨 UI/UX Features

### Modern Design Elements
- **Gradient Backgrounds**: Sophisticated color schemes
- **Glass Morphism**: Backdrop blur effects
- **Responsive Layout**: Mobile-first design
- **Micro-interactions**: Smooth hover and transition effects
- **Real-time Feedback**: Processing status with visual indicators

### Accessibility Features  
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and semantic HTML
- **High Contrast**: Proper color contrast ratios
- **Focus Indicators**: Clear focus states for all interactive elements

## 📊 API Endpoints

### User Management
- `POST /api/users` - Create new user
- `GET /api/users/{user_id}` - Get user profile
- `POST /api/users/{user_id}/assessment` - Save learning assessment

### Learning Kits
- `POST /api/kit/create` - Create learning kit (with real-time logs)
- `GET /api/users/{user_id}/learning-kits` - Get user's kits
- `GET /api/learning-kits/{kit_id}` - Get specific kit details

### Study Sessions & QA
- `POST /api/users/{user_id}/study-session` - Start study session
- `POST /api/qa-sessions` - Ask questions about content
- `GET /api/users/{user_id}/analytics` - Get user analytics

### Assessment
- `GET /api/learning-assessment-questions` - Get assessment questions

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
```

#### Frontend (.env)  
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### MongoDB Collections
- **users**: User profiles and preferences
- **assessments**: Learning style assessment results
- **learning_kits**: Generated content and metadata
- **study_sessions**: Session data and recommendations
- **qa_sessions**: Question-answer history

## 🤖 Local AI Implementation

### Content Generation Process
1. **Text Analysis**: Extract key concepts and sentences
2. **Style Adaptation**: Format content based on learning preference
3. **Intelligent Processing**: Create summaries, questions, and activities
4. **Quality Enhancement**: Add metadata, hints, and formatting
5. **Real-time Logging**: Provide status updates during generation

### Processing Steps (Visible to Users)
- **Initializing**: Setting up generation pipeline
- **Summarizing**: Creating style-specific summaries
- **Flashcards**: Generating Q&A pairs with hints
- **Audio**: Writing conversational lesson scripts
- **Doodle**: Creating visual drawing instructions
- **QA Index**: Building searchable knowledge base

## 🚀 Deployment

### Local Development
```bash
# Start all services
python backend/server.py &
cd frontend && yarn start
```

### Production Deployment
1. **Build Frontend**: `yarn build` in frontend directory
2. **Configure Reverse Proxy**: nginx or Apache for static files
3. **Process Management**: Use supervisor, pm2, or systemd
4. **Database**: Set up production MongoDB instance
5. **Environment**: Configure production environment variables

## 📈 Performance Features

### Backend Optimizations
- **Async/Await**: Non-blocking database operations
- **Connection Pooling**: Efficient MongoDB connections
- **Request Validation**: Pydantic models for type safety
- **Error Handling**: Comprehensive exception management

### Frontend Optimizations  
- **Code Splitting**: Lazy loading for better performance
- **Optimized Images**: Compressed assets and icons
- **Caching Strategy**: localStorage for user sessions
- **Bundle Size**: Tree-shaking and minimal dependencies

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check MongoDB connection
mongosh --eval "db.runCommand('ping')"

# Verify Python dependencies
pip list | grep fastapi

# Check port availability
lsof -i :8001
```

#### Frontend Build Errors
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
yarn install

# Check React version compatibility
yarn list react
```

#### Database Connection Issues
```bash
# Restart MongoDB
sudo systemctl restart mongod

# Check MongoDB logs
tail -f /var/log/mongodb/mongod.log
```

## 🎓 Educational Benefits

### For Students
- **Personalized Learning**: Content adapted to individual preferences
- **Multi-modal Content**: Various formats for different learning styles
- **Progress Tracking**: Clear insights into learning patterns
- **Self-Paced**: Learn at your own speed and schedule

### For Educators
- **Content Generation**: Quickly create diverse learning materials
- **Student Analytics**: Understand learning preferences and progress
- **Accessibility**: Support for different learning needs
- **Time Saving**: Automated content creation and organization

## 📝 License & Credits

### Open Source Components
- **React**: MIT License
- **FastAPI**: MIT License  
- **MongoDB**: Server Side Public License
- **Tailwind CSS**: MIT License
- **shadcn/ui**: MIT License

### Academic Use
This project is designed for educational purposes and final-year projects. Feel free to use, modify, and extend the codebase for learning and academic research.

## 🤝 Contributing

### Development Workflow
1. **Fork Repository**: Create your own fork
2. **Feature Branch**: Create feature-specific branches
3. **Local Testing**: Run full test suite before committing
4. **Pull Request**: Submit with clear description of changes

### Code Standards
- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Use ESLint and Prettier formatting
- **Git Commits**: Clear, descriptive commit messages
- **Documentation**: Update README for new features

---

**EduCrate** - Transforming education through intelligent, personalized learning experiences! 🎓✨