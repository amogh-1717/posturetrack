import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app">
      <header className="app-header">
        <h1>PostureTrack Dashboard</h1>
        <p>Real-time posture monitoring</p>
      </header>
      <main className="app-main">
        <Dashboard />
      </main>
    </div>
  );
};

export default App;

