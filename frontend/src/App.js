import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Import shadcn/ui components
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { RadioGroup, RadioGroupItem } from './components/ui/radio-group';
import { Progress } from './components/ui/progress';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { AlertDialog, AlertDialogAction, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from './components/ui/alert-dialog';

// Import icons from lucide-react
import { BookOpen, Brain, Headphones, Eye, Zap, Clock, MessageCircle, TrendingUp, User, Settings, Plus, Search, Play, Download, Star } from 'lucide-react';

// Configure axios
const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'
});

// Main App Component
function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('welcome');
  const [learningKits, setLearningKits] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Check for existing user in localStorage
    const savedUser = localStorage.getItem('educrate_user');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
      setCurrentView('dashboard');
      loadUserKits(JSON.parse(savedUser).id);
    }
  }, []);

  const loadUserKits = async (userId) => {
    try {
      const response = await api.get(`/api/users/${userId}/learning-kits`);
      setLearningKits(response.data.kits);
    } catch (error) {
      console.error('Error loading kits:', error);
    }
  };

  const handleUserCreated = (user) => {
    setCurrentUser(user);
    localStorage.setItem('educrate_user', JSON.stringify(user));
    setCurrentView('assessment');
  };

  const handleAssessmentComplete = (results) => {
    setCurrentView('dashboard');
    loadUserKits(currentUser.id);
  };

  const handleLogout = () => {
    localStorage.removeItem('educrate_user');
    setCurrentUser(null);
    setCurrentView('welcome');
    setLearningKits([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b border-indigo-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  EduCrate
                </h1>
                <p className="text-sm text-gray-600">Intelligent Learning Platform</p>
              </div>
            </div>
            {currentUser && (
              <div className="flex items-center gap-4">
                <Avatar>
                  <AvatarFallback>{currentUser.name.charAt(0)}</AvatarFallback>
                </Avatar>
                <div className="text-right">
                  <p className="font-medium">{currentUser.name}</p>
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    Logout
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {currentView === 'welcome' && (
          <WelcomeView onUserCreated={handleUserCreated} />
        )}
        {currentView === 'assessment' && currentUser && (
          <AssessmentView 
            user={currentUser} 
            onComplete={handleAssessmentComplete}
          />
        )}
        {currentView === 'dashboard' && currentUser && (
          <DashboardView 
            user={currentUser}
            kits={learningKits}
            onKitCreated={() => loadUserKits(currentUser.id)}
          />
        )}
      </main>
    </div>
  );
}

// Welcome/Onboarding Component
function WelcomeView({ onUserCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    preferred_language: 'en',
    timezone: 'UTC'
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const userData = {
        ...formData,
        learning_styles: [] // Will be determined by assessment
      };

      const response = await api.post('/api/users', userData);
      
      if (response.data.user_id) {
        const newUser = { ...userData, id: response.data.user_id };
        onUserCreated(newUser);
      }
    } catch (error) {
      console.error('Error creating user:', error);
      alert('Error creating user. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-100 rounded-full mb-6">
          <Brain className="w-5 h-5 text-indigo-600" />
          <span className="text-indigo-600 font-medium">AI-Powered Education</span>
        </div>
        
        <h1 className="text-5xl font-bold mb-6 leading-tight">
          Personalized Learning
          <span className="block bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Tailored to Your Style
          </span>
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
          EduCrate creates intelligent learning kits with AI-generated summaries, flashcards, 
          audio lessons, and visual doodles - all adapted to your unique learning preferences.
        </p>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardHeader className="pb-4">
              <Eye className="w-12 h-12 text-indigo-600 mx-auto mb-4" />
              <CardTitle className="text-lg">Visual Learning</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">Doodle-style illustrations and mind maps that make complex concepts visual and memorable.</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-gradient-to-br from-purple-50 to-pink-50">
            <CardHeader className="pb-4">
              <Headphones className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <CardTitle className="text-lg">Audio Lessons</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">AI-generated audio content perfect for auditory learners and on-the-go studying.</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-gradient-to-br from-green-50 to-teal-50">
            <CardHeader className="pb-4">
              <Brain className="w-12 h-12 text-teal-600 mx-auto mb-4" />
              <CardTitle className="text-lg">Smart Flashcards</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">Interactive flashcards generated from your content with spaced repetition algorithms.</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Registration Form */}
      <Card className="max-w-md mx-auto shadow-xl border-0 bg-white/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Get Started</CardTitle>
          <CardDescription>Create your personalized learning profile</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="language">Preferred Language</Label>
              <Select value={formData.preferred_language} onValueChange={(value) => setFormData({...formData, preferred_language: value})}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Spanish</SelectItem>
                  <SelectItem value="fr">French</SelectItem>
                  <SelectItem value="de">German</SelectItem>
                  <SelectItem value="zh">Chinese</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button type="submit" className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700" disabled={isLoading}>
              {isLoading ? 'Creating Account...' : 'Start Your Learning Journey'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

// Learning Style Assessment Component
function AssessmentView({ user, onComplete }) {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      const response = await api.get('/api/learning-assessment-questions');
      setQuestions(response.data.questions);
    } catch (error) {
      console.error('Error loading questions:', error);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers({...answers, [questionId]: answer});
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      submitAssessment();
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const submitAssessment = async () => {
    setIsLoading(true);

    try {
      // Calculate scores for each learning style
      const scores = { visual: 0, auditory: 0, textual: 0, kinesthetic: 0 };
      
      Object.values(answers).forEach(answer => {
        scores[answer] = (scores[answer] || 0) + 2;
      });

      const assessmentData = {
        user_id: user.id,
        visual_score: scores.visual || 4,
        auditory_score: scores.auditory || 4,
        textual_score: scores.textual || 4,
        kinesthetic_score: scores.kinesthetic || 4,
        answers
      };

      await api.post(`/api/users/${user.id}/assessment`, assessmentData);
      onComplete();
    } catch (error) {
      console.error('Error submitting assessment:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (questions.length === 0) {
    return <div className="text-center py-8">Loading assessment...</div>;
  }

  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const question = questions[currentQuestion];

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center justify-between mb-4">
            <Badge variant="outline">
              Question {currentQuestion + 1} of {questions.length}
            </Badge>
            <div className="text-sm text-gray-500">Learning Style Assessment</div>
          </div>
          <Progress value={progress} className="mb-4" />
          <CardTitle className="text-xl">{question.question}</CardTitle>
        </CardHeader>
        <CardContent>
          <RadioGroup 
            value={answers[question.id] || ''} 
            onValueChange={(value) => handleAnswer(question.id, value)}
            className="space-y-4"
          >
            {question.options.map((option, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors">
                <RadioGroupItem value={option.value} id={`${question.id}-${index}`} className="mt-1" />
                <Label htmlFor={`${question.id}-${index}`} className="flex-1 cursor-pointer leading-relaxed">
                  {option.text}
                </Label>
              </div>
            ))}
          </RadioGroup>

          <div className="flex justify-between mt-8">
            <Button 
              variant="outline" 
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
            >
              Previous
            </Button>
            
            <Button 
              onClick={handleNext}
              disabled={!answers[question.id]}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
            >
              {isLoading ? 'Submitting...' : 
                currentQuestion === questions.length - 1 ? 'Complete Assessment' : 'Next'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Dashboard Component
function DashboardView({ user, kits, onKitCreated }) {
  const [activeTab, setActiveTab] = useState('create');
  const [isCreating, setIsCreating] = useState(false);
  
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="text-center py-8">
        <h2 className="text-4xl font-bold mb-4">
          Welcome back, <span className="text-indigo-600">{user.name}</span>!
        </h2>
        <p className="text-gray-600 text-lg">Ready to create personalized learning experiences?</p>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-indigo-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Learning Kits</p>
                <p className="text-3xl font-bold text-indigo-600">{kits.length}</p>
              </div>
              <BookOpen className="w-12 h-12 text-indigo-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-pink-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Learning Styles</p>
                <p className="text-3xl font-bold text-purple-600">{user.learning_styles?.length || 0}</p>
              </div>
              <Brain className="w-12 h-12 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-teal-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Study Sessions</p>
                <p className="text-3xl font-bold text-teal-600">0</p>
              </div>
              <TrendingUp className="w-12 h-12 text-teal-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="create">Create Kit</TabsTrigger>
          <TabsTrigger value="kits">My Kits</TabsTrigger>
          <TabsTrigger value="study">Study Session</TabsTrigger>
        </TabsList>

        <TabsContent value="create" className="mt-6">
          <CreateKitView user={user} onKitCreated={onKitCreated} />
        </TabsContent>

        <TabsContent value="kits" className="mt-6">
          <MyKitsView kits={kits} />
        </TabsContent>

        <TabsContent value="study" className="mt-6">
          <StudySessionView user={user} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Create Kit Component
function CreateKitView({ user, onKitCreated }) {
  const [formData, setFormData] = useState({
    topic: '',
    source_content: '',
    target_styles: user.learning_styles || []
  });
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsCreating(true);

    try {
      const params = new URLSearchParams({
        user_id: user.id,
        topic: formData.topic,
        source_content: formData.source_content
      });

      formData.target_styles.forEach(style => {
        params.append('target_styles', style);
      });

      const response = await api.post(`/api/learning-kits?${params}`);
      
      if (response.data.kit) {
        alert('Learning kit created successfully!');
        setFormData({ topic: '', source_content: '', target_styles: user.learning_styles || [] });
        onKitCreated();
      }
    } catch (error) {
      console.error('Error creating kit:', error);
      alert('Error creating kit. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <Plus className="w-6 h-6" />
          Create New Learning Kit
        </CardTitle>
        <CardDescription>
          Generate personalized content based on your learning style preferences
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="topic">Learning Topic</Label>
            <Input
              id="topic"
              value={formData.topic}
              onChange={(e) => setFormData({...formData, topic: e.target.value})}
              placeholder="e.g., Machine Learning Basics, Photosynthesis, World War II"
              required
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="content">Source Content</Label>
            <Textarea
              id="content"
              value={formData.source_content}
              onChange={(e) => setFormData({...formData, source_content: e.target.value})}
              placeholder="Paste your study material, article, or notes here..."
              required
              className="mt-1 min-h-[200px]"
            />
          </div>

          <div>
            <Label>Learning Styles (Your Preferences)</Label>
            <div className="mt-2 flex flex-wrap gap-2">
              {(user.learning_styles || []).map(style => (
                <Badge key={style} variant="secondary" className="px-3 py-1">
                  {style.charAt(0).toUpperCase() + style.slice(1)}
                </Badge>
              ))}
            </div>
            {(!user.learning_styles || user.learning_styles.length === 0) && (
              <p className="text-sm text-gray-500 mt-2">
                Complete the learning assessment to get personalized content recommendations.
              </p>
            )}
          </div>

          <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700" 
            disabled={isCreating}
          >
            {isCreating ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Generating Content...
              </div>
            ) : (
              'Create Learning Kit'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

// My Kits Component
function MyKitsView({ kits }) {
  const [selectedKit, setSelectedKit] = useState(null);

  return (
    <div className="space-y-6">
      {kits.length === 0 ? (
        <Card className="text-center py-12 border-dashed">
          <CardContent>
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-600 mb-2">No Learning Kits Yet</h3>
            <p className="text-gray-500">Create your first learning kit to get started!</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {kits.map(kit => (
            <Card key={kit.id} className="hover:shadow-lg transition-shadow cursor-pointer border-0 shadow-md" onClick={() => setSelectedKit(kit)}>
              <CardHeader>
                <CardTitle className="text-lg line-clamp-2">{kit.topic}</CardTitle>
                <CardDescription>
                  {kit.content_items?.length || 0} content items • {kit.estimated_time} min
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1 mb-4">
                  {(kit.learning_styles || []).map(style => (
                    <Badge key={style} variant="outline" className="text-xs">
                      {style}
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-gray-600 line-clamp-3">
                  {kit.source_content?.substring(0, 120)}...
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {selectedKit && (
        <KitDetailView kit={selectedKit} onClose={() => setSelectedKit(null)} />
      )}
    </div>
  );
}

// Kit Detail Component
function KitDetailView({ kit, onClose }) {
  return (
    <AlertDialog open={true} onOpenChange={onClose}>
      <AlertDialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-2xl">{kit.topic}</AlertDialogTitle>
          <AlertDialogDescription className="text-base">
            Created on {new Date(kit.created_at).toLocaleDateString()}
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="space-y-6">
          <div className="flex flex-wrap gap-2">
            {(kit.learning_styles || []).map(style => (
              <Badge key={style} className="px-3 py-1">
                {style.charAt(0).toUpperCase() + style.slice(1)}
              </Badge>
            ))}
          </div>

          {(kit.content_items || []).map((item, index) => (
            <Card key={index} className="border border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  {item.type === 'summary' && <BookOpen className="w-5 h-5" />}
                  {item.type === 'flashcards' && <Brain className="w-5 h-5" />}
                  {item.type === 'audio_lesson' && <Headphones className="w-5 h-5" />}
                  {item.type === 'visual_doodle' && <Eye className="w-5 h-5" />}
                  {item.type.replace('_', ' ').toUpperCase()}
                </CardTitle>
                <CardDescription>
                  For {item.learning_style} learners
                </CardDescription>
              </CardHeader>
              <CardContent>
                {item.type === 'flashcards' ? (
                  <div className="space-y-2">
                    {(item.content || []).slice(0, 3).map((card, cardIndex) => (
                      <div key={cardIndex} className="p-3 bg-gray-50 rounded-lg">
                        <p className="font-medium text-sm">{card.question}</p>
                        <p className="text-sm text-gray-600 mt-1">{card.answer}</p>
                      </div>
                    ))}
                    {item.content?.length > 3 && (
                      <p className="text-sm text-gray-500">+ {item.content.length - 3} more cards</p>
                    )}
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <p className="whitespace-pre-wrap">{item.content}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        <AlertDialogFooter>
          <AlertDialogAction onClick={onClose}>Close</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// Study Session Component
function StudySessionView({ user }) {
  const [sessionData, setSessionData] = useState({
    mood: '',
    available_time: 30,
    energy_level: 5,
    focus_level: 5
  });
  const [isStarting, setIsStarting] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);

  const moods = [
    { value: 'focused', label: 'Focused', icon: '🎯' },
    { value: 'relaxed', label: 'Relaxed', icon: '😌' },
    { value: 'energetic', label: 'Energetic', icon: '⚡' },
    { value: 'stressed', label: 'Stressed', icon: '😰' },
    { value: 'curious', label: 'Curious', icon: '🤔' }
  ];

  const handleStartSession = async () => {
    setIsStarting(true);
    try {
      const response = await api.post(`/api/users/${user.id}/study-session`, {
        ...sessionData,
        user_id: user.id,
        preferred_content_types: ['summary', 'flashcards']
      });
      
      setCurrentSession(response.data);
    } catch (error) {
      console.error('Error starting session:', error);
    } finally {
      setIsStarting(false);
    }
  };

  if (currentSession) {
    return (
      <Card className="shadow-lg border-0 bg-gradient-to-br from-green-50 to-teal-50">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Zap className="w-6 h-6 text-teal-600" />
            Study Session Active
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-white rounded-lg">
                <h4 className="font-medium text-teal-800 mb-2">AI Recommendations</h4>
                <p className="text-sm text-gray-600">
                  {currentSession.suggestions.motivation_message}
                </p>
              </div>
              <div className="p-4 bg-white rounded-lg">
                <h4 className="font-medium text-teal-800 mb-2">Suggested Duration</h4>
                <p className="text-sm text-gray-600">
                  {currentSession.suggestions.study_duration} minutes with {currentSession.suggestions.break_intervals} min breaks
                </p>
              </div>
            </div>
            
            <Button 
              variant="outline" 
              onClick={() => setCurrentSession(null)}
              className="w-full"
            >
              End Session
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <Clock className="w-6 h-6" />
          Start Study Session
        </CardTitle>
        <CardDescription>
          Get personalized recommendations based on your current state
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <Label>How are you feeling right now?</Label>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-2">
            {moods.map(mood => (
              <Button
                key={mood.value}
                variant={sessionData.mood === mood.value ? "default" : "outline"}
                onClick={() => setSessionData({...sessionData, mood: mood.value})}
                className="h-auto p-4 flex flex-col gap-2"
              >
                <span className="text-2xl">{mood.icon}</span>
                <span className="text-sm">{mood.label}</span>
              </Button>
            ))}
          </div>
        </div>

        <div>
          <Label>Available Study Time (minutes)</Label>
          <Select value={sessionData.available_time.toString()} onValueChange={(value) => setSessionData({...sessionData, available_time: parseInt(value)})}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="15">15 minutes</SelectItem>
              <SelectItem value="30">30 minutes</SelectItem>
              <SelectItem value="45">45 minutes</SelectItem>
              <SelectItem value="60">1 hour</SelectItem>
              <SelectItem value="90">1.5 hours</SelectItem>
              <SelectItem value="120">2 hours</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <Label>Energy Level</Label>
            <div className="mt-2 flex items-center gap-4">
              <span className="text-sm text-gray-500">Low</span>
              <input
                type="range"
                min="1"
                max="10"
                value={sessionData.energy_level}
                onChange={(e) => setSessionData({...sessionData, energy_level: parseInt(e.target.value)})}
                className="flex-1"
              />
              <span className="text-sm text-gray-500">High</span>
              <Badge variant="secondary">{sessionData.energy_level}/10</Badge>
            </div>
          </div>

          <div>
            <Label>Focus Level</Label>
            <div className="mt-2 flex items-center gap-4">
              <span className="text-sm text-gray-500">Low</span>
              <input
                type="range"
                min="1"
                max="10"
                value={sessionData.focus_level}
                onChange={(e) => setSessionData({...sessionData, focus_level: parseInt(e.target.value)})}
                className="flex-1"
              />
              <span className="text-sm text-gray-500">High</span>
              <Badge variant="secondary">{sessionData.focus_level}/10</Badge>
            </div>
          </div>
        </div>

        <Button 
          onClick={handleStartSession}
          disabled={!sessionData.mood || isStarting}
          className="w-full bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700"
        >
          {isStarting ? 'Starting Session...' : 'Start Smart Study Session'}
        </Button>
      </CardContent>
    </Card>
  );
}

export default App;