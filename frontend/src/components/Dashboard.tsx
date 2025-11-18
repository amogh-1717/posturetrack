import React, { useState, useEffect } from 'react';
import PostureStatus from './PostureStatus';
import './Dashboard.css';

interface PostureRecord {
  id: number;
  status: string;
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const [currentStatus, setCurrentStatus] = useState<string>('unknown');
  const [recentRecords, setRecentRecords] = useState<PostureRecord[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Fetch initial data
  const fetchRecentRecords = async () => {
    try {
      const response = await fetch('/records/recent?limit=5');
      if (response.ok) {
        const records = await response.json();
        setRecentRecords(records);
        if (records.length > 0) {
          setCurrentStatus(records[0].status);
        }
      }
    } catch (error) {
      console.error('Failed to fetch recent records:', error);
    }
  };

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
      
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        setWs(websocket);
      };
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received posture update:', data);
          
          // Update current status
          setCurrentStatus(data.status);
          
          // Add to recent records and keep only last 5
          setRecentRecords(prev => {
            const newRecords = [data, ...prev].slice(0, 5);
            return newRecords;
          });
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        setWs(null);
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };
    };

    // Initial data fetch
    fetchRecentRecords();
    
    // Connect WebSocket
    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const getConnectionStatusClass = () => {
    switch (connectionStatus) {
      case 'connected': return 'connected';
      case 'connecting': return 'connecting';
      case 'disconnected': return 'disconnected';
      default: return 'disconnected';
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className={`connection-status ${getConnectionStatusClass()}`}>
          <span className="status-indicator"></span>
          <span className="status-text">
            {connectionStatus === 'connected' ? 'Live' : 
             connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="dashboard-content">
        <PostureStatus 
          currentStatus={currentStatus}
          recentRecords={recentRecords}
        />
      </div>

      <div className="dashboard-footer">
        <p>
          {connectionStatus === 'connected' 
            ? 'Receiving live updates from pose detection'
            : 'Waiting for pose detection client...'
          }
        </p>
      </div>
    </div>
  );
};

export default Dashboard;