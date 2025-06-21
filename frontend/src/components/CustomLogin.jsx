import React, { useState } from 'react';
import { signIn, signUp, confirmSignUp } from 'aws-amplify/auth';
import { Bot, User, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import './CustomLogin.css';

export default function CustomLogin({ onSignIn }) {
  const [mode, setMode] = useState('signin'); // signin, signup, confirm
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    confirmationCode: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'signin') {
        const user = await signIn({
          username: formData.email,
          password: formData.password
        });
        onSignIn(user);
      } else if (mode === 'signup') {
        await signUp({
          username: formData.email, // Use email as username
          password: formData.password,
          options: { userAttributes: { email: formData.email } }
        });
        setMode('confirm');
      } else if (mode === 'confirm') {
        await confirmSignUp({
          username: formData.email,
          confirmationCode: formData.confirmationCode
        });
        setMode('signin');
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        <div className="login-header">
          <div className="bot-avatar">
            <Bot className="bot-icon" />
          </div>
          <h1 className="login-title">Link</h1>
          <p className="login-subtitle">
            {mode === 'signin' && 'Sign in to continue'}
            {mode === 'signup' && 'Create your account'}
            {mode === 'confirm' && 'Verify your email'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}

          <div className="input-group">
            <Mail className="input-icon" />
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
          </div>

          {mode !== 'confirm' && (
            <div className="input-group">
              <Lock className="input-icon" />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
              />
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          )}

          {mode === 'confirm' && (
            <div className="input-group">
              <input
                type="text"
                placeholder="Confirmation Code"
                value={formData.confirmationCode}
                onChange={(e) => setFormData({...formData, confirmationCode: e.target.value})}
                required
              />
            </div>
          )}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Loading...' : 
             mode === 'signin' ? 'Sign In' :
             mode === 'signup' ? 'Create Account' : 'Verify'}
          </button>

          <div className="mode-switch">
            {mode === 'signin' && (
              <button type="button" onClick={() => setMode('signup')}>
                Need an account? Sign up
              </button>
            )}
            {mode === 'signup' && (
              <button type="button" onClick={() => setMode('signin')}>
                Already have an account? Sign in
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}