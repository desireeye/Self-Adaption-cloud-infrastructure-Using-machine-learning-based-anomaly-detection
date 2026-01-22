/**
 * Main App Component
 */
import React, { useEffect } from 'react';
import { Dashboard } from './pages/Dashboard';
import './styles/globals.css';

function App() {
  useEffect(() => {
    // Ensure API URL is set
    if (!process.env.REACT_APP_API_URL) {
      console.warn('REACT_APP_API_URL not set, using default: http://localhost:8000');
    }
  }, []);

  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
