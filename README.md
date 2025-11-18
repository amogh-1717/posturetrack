# PostureTrack - AI-Powered Ergonomic Monitoring for Surgical Training

Real-time posture monitoring system designed to help surgical residents develop proper ergonomics and prevent musculoskeletal injuries during training.

---

## 🎯 Problem

Surgical residents spend 10+ years training in positions that cause chronic musculoskeletal injuries. Poor ergonomics during training leads to career-ending injuries, but there's no scalable way to monitor and correct posture in real-time across hundreds of training sessions.

## 💡 Solution

PostureTrack uses computer vision to monitor critical ergonomic metrics at 30 FPS, providing real-time feedback during surgical training. The system tracks wrist flexion, neck alignment, and spine posture to identify injury risks before they become chronic problems.

---

## 🛠️ My Contributions (Backend Focus)

I built the complete backend architecture for this project:

- **FastAPI Backend** - Designed and implemented RESTful API with WebSocket support for real-time data streaming
- **WebSocket Architecture** - Built sub-100ms latency streaming system for live posture data from computer vision client to frontend  
- **Database Design** - Created PostgreSQL schema to capture 10,000+ measurements per training session for longitudinal analysis
- **Real-time Processing** - Implemented data pipeline handling 30 FPS pose data with metric calculations and alert generation

> **Note:** Computer vision components (OpenCV/MediaPipe integration) were implemented by teammates.

---

## 🔧 Tech Stack

### Backend (My Work)
- FastAPI
- WebSocket  
- PostgreSQL
- Python

### Computer Vision (Teammate)
- OpenCV
- MediaPipe

### Frontend (Teammate)
- React

---

## 📁 Project Structure
```
posturetrack/
├── backend/        # FastAPI server, WebSocket manager, database models
├── frontend/       # React dashboard (teammate's work)
└── pose_client/    # Computer vision processing (teammate's work)
```

---

## 🚀 Installation

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Database Setup

Requires PostgreSQL. Update connection string in `database.py`.

---

## 📊 Impact

- ✅ Tracks 10,000+ measurements per session for injury risk analysis
- ✅ Provides real-time ergonomic alerts during training  
- ✅ Enables data-driven feedback for surgical residents

---

**Built for Incubate National MedTech Hackathon**
