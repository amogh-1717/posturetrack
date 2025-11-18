import React from 'react';
import './PostureStatus.css';

interface PostureRecord {
  id: number;
  status: string;
  timestamp: string;
}

interface PostureStatusProps {
  currentStatus: string;
  recentRecords: PostureRecord[];
}

const PostureStatus: React.FC<PostureStatusProps> = ({ currentStatus, recentRecords }) => {
  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return 'Invalid time';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'good': return '✅';
      case 'ok': return '⚠️';
      case 'bad': return '❌';
      default: return '❓';
    }
  };

  const getStatusMessage = (status: string): string => {
    switch (status) {
      case 'good': return 'Excellent posture! Keep it up!';
      case 'ok': return 'Good, but room for improvement';
      case 'bad': return 'Please adjust your posture';
      default: return 'Waiting for posture data...';
    }
  };

  return (
    <div className="posture-status">
      {/* Current Status */}
      <div className={`current-status ${currentStatus}`}>
        <div className="status-icon">
          {getStatusIcon(currentStatus)}
        </div>
        <div className="status-content">
          <h2 className="status-title">
            Current Posture: <span className="status-value">{currentStatus.toUpperCase()}</span>
          </h2>
          <p className="status-message">{getStatusMessage(currentStatus)}</p>
        </div>
      </div>

      {/* Recent Records */}
      <div className="recent-records">
        <h3>Recent Activity</h3>
        {recentRecords.length === 0 ? (
          <div className="no-records">
            <p>No recent posture data available</p>
          </div>
        ) : (
          <div className="records-list">
            {recentRecords.map((record) => (
              <div key={record.id} className={`record-item ${record.status}`}>
                <span className="record-icon">{getStatusIcon(record.status)}</span>
                <span className="record-status">{record.status}</span>
                <span className="record-time">{formatTimestamp(record.timestamp)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className="posture-stats">
        <h3>Session Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Total Records:</span>
            <span className="stat-value">{recentRecords.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Good Posture:</span>
            <span className="stat-value good">
              {recentRecords.filter(r => r.status === 'good').length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Needs Improvement:</span>
            <span className="stat-value bad">
              {recentRecords.filter(r => r.status === 'bad').length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostureStatus;