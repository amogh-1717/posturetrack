from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging

from database import get_db, engine
from models import Base
import crud
import schemas
from websocket_manager import manager

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PostureTrack API", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PostureTrack API is running"}

@app.get("/records/recent", response_model=list[schemas.PostureRecord])
async def get_recent_records(limit: int = 5, db: Session = Depends(get_db)):
    """Get recent posture records"""
    records = crud.get_recent_records(db, limit=limit)
    return records

@app.websocket("/ws/posture")
async def posture_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for posture updates from pose client"""
    await websocket.accept()
    logger.info("Pose client connected")
    
    try:
        while True:
            # Receive data from pose client
            data = await websocket.receive_text()
            logger.info(f"Received posture data: {data}")
            
            try:
                posture_data = json.loads(data)
                
                # Create record in database
                record_create = schemas.PostureRecordCreate(
                    status=posture_data["status"],
                    timestamp=datetime.fromisoformat(posture_data["timestamp"].replace("Z", "+00:00"))
                )
                db_record = crud.create_posture_record(db, record_create)
                
                # Broadcast to frontend clients
                await manager.broadcast_to_frontends({
                    "id": db_record.id,
                    "status": db_record.status,
                    "timestamp": db_record.timestamp.isoformat()
                })
                
                # Send acknowledgment back to pose client
                await websocket.send_text(json.dumps({"status": "received"}))
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"Invalid posture data format: {e}")
                await websocket.send_text(json.dumps({"error": "Invalid data format"}))
                
    except WebSocketDisconnect:
        logger.info("Pose client disconnected")
    except Exception as e:
        logger.error(f"Error in posture websocket: {e}")

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint for frontend dashboard"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)