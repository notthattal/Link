import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Amplify } from 'aws-amplify';
import { signIn, signOut, getCurrentUser } from 'aws-amplify/auth';
import Chatbot from './components/Chatbot';
import ConnectApps from './components/ConnectApps.jsx';
import CustomLogin from './components/CustomLogin.jsx';
import OAuthCallback from './components/OAuthCallback.jsx';
import awsConfig from './aws-config';
import './App.css';

Amplify.configure(awsConfig);

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    }
    setLoading(false);
  };

  const handleSignOut = async () => {
    await signOut();
    setUser(null);
  };

  return (
    <div className="App">
      <Router>
        {user ? (
          <Routes>
            <Route path="/" element={<Chatbot user={user} signOut={handleSignOut} />} />
            <Route path="/connect-apps" element={<ConnectApps user={user} />} />
            <Route path="/callback/:service" element={<OAuthCallback user={user} />} />
          </Routes>
        ) : (
          <CustomLogin onSignIn={setUser} />
        )}
      </Router>
    </div>
  );
}

export default App;