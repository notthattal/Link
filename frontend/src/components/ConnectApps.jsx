import React, { useState, useEffect } from 'react';
import { X, Search, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { fetchAuthSession } from 'aws-amplify/auth';
import './ConnectApps.css';

const ConnectApps = ({ user }) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [userConnections, setUserConnections] = useState([]);

  const connections = [
    { 
      name: 'Gmail', 
      connected: false, 
      category: 'Email',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg',
      brandColor: '#FF3D57'
    },
    { 
      name: 'Google Calendar', 
      connected: false, 
      category: 'Productivity',
      logo: 'https://ssl.gstatic.com/calendar/images/dynamiclogo_2020q4/calendar_31_2x.png',
      brandColor: '#4285F4'
    },
    { 
      name: 'Google Drive', 
      connected: false, 
      category: 'Storage',
      logo: 'https://ssl.gstatic.com/images/branding/product/1x/drive_2020q4_32dp.png',
      brandColor: '#4285F4'
    },
    { 
      name: 'Spotify', 
      connected: false, 
      category: 'Entertainment',
      logo: '/assets/spotify_logo.png',
      brandColor: '#1DB954'
    },
    { 
      name: 'Figma', 
      connected: false, 
      category: 'Design',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/3/33/Figma-logo.svg',
      brandColor: '#F24E1E'
    },
    { 
      name: 'Google', 
      connected: false, 
      category: 'Productivity',
      logo: 'https://logo.clearbit.com/google.com',
      brandColor: '#4285F4'
    },
    { 
      name: 'Instacart', 
      connected: false, 
      category: 'Shopping',
      logo: '/assets/instacart_logo.svg',
      brandColor: '#43B02A'
    },
    { 
      name: 'Jira', 
      connected: false, 
      category: 'Project Management',
      logo: 'https://logo.clearbit.com/atlassian.com',
      brandColor: '#0052CC'
    },
    { 
      name: 'Linear', 
      connected: false, 
      category: 'Project Management',
      logo: 'https://logo.clearbit.com/linear.app',
      brandColor: '#5E6AD2'
    },
    { 
      name: 'Notion', 
      connected: false, 
      category: 'Productivity',
      logo: '/assets/notion_logo.svg',
      brandColor: '#000000'
    },
    { 
      name: 'Slack', 
      connected: false, 
      category: 'Communication',
      logo: 'https://logo.clearbit.com/slack.com',
      brandColor: '#4A154B'
    },
    { 
      name: 'Amazon', 
      connected: false, 
      category: 'Shopping',
      logo: 'https://logo.clearbit.com/amazon.com',
      brandColor: '#FF9900'
    },
    { 
      name: 'Brex', 
      connected: false, 
      category: 'Finance',
      logo: 'https://logo.clearbit.com/brex.com',
      brandColor: '#FF6B6B'
    },
    { 
      name: 'Canva', 
      connected: false, 
      category: 'Design',
      logo: 'https://logo.clearbit.com/canva.com',
      brandColor: '#00C4CC'
    },
    { 
      name: 'Capital One', 
      connected: false, 
      category: 'Finance',
      logo: 'https://logo.clearbit.com/capitalone.com',
      brandColor: '#004879'
    },
    { 
      name: 'Coinbase', 
      connected: false, 
      category: 'Finance',
      logo: 'https://logo.clearbit.com/coinbase.com',
      brandColor: '#0052FF'
    },
    { 
      name: 'Delta', 
      connected: false, 
      category: 'Travel',
      logo: 'https://logo.clearbit.com/delta.com',
      brandColor: '#CE1126'
    },
    { 
      name: 'Dropbox', 
      connected: false, 
      category: 'Storage',
      logo: 'https://logo.clearbit.com/dropbox.com',
      brandColor: '#0061FF'
    },
    { 
      name: 'Google Maps',  
      connected: false, 
      category: 'Navigation',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/b/bd/Google_Maps_Logo_2020.svg',
      brandColor: '#4285F4'
    },
    { 
      name: 'GitHub', 
      connected: false, 
      category: 'Development',
      logo: 'https://logo.clearbit.com/github.com',
      brandColor: '#181717'
    },
    { 
      name: 'GitLab', 
      connected: false, 
      category: 'Development',
      logo: 'https://logo.clearbit.com/gitlab.com',
      brandColor: '#FC6D26'
    },
    { 
      name: 'LinkedIn', 
      connected: false, 
      category: 'Professional',
      logo: 'https://logo.clearbit.com/linkedin.com',
      brandColor: '#0A66C2'
    },
    { 
      name: 'Lyft', 
      connected: false, 
      category: 'Transportation',
      logo: 'https://logo.clearbit.com/lyft.com',
      brandColor: '#FF00BF'
    },
    { 
      name: 'Microsoft Outlook', 
      connected: false, 
      category: 'Email',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/d/df/Microsoft_Office_Outlook_%282018%E2%80%93present%29.svg',
      brandColor: '#0078D4'
    }
  ];

  // Fetch user's connected apps
  useEffect(() => {
    const fetchUserConnections = async () => {
      try {
        const session = await fetchAuthSession();
        const token = session.tokens.idToken.toString();
        
        const response = await fetch('/api/user/get_connections', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const connectedApps = await response.json();
          setUserConnections(connectedApps);
        }
      } catch (error) {
        console.error('Error fetching connections:', error);
      }
    };

    if (user) {
      fetchUserConnections();
    }
  }, [user]);

  // Update connections with user's actual connection status
  const connectionsWithStatus = connections.map(connection => ({
    ...connection,
    connected: userConnections.includes(connection.name.toLowerCase())
  }));

  const filteredConnections = connectionsWithStatus.filter(connection =>
    connection.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSpotifyConnect = () => {
    const clientId = import.meta.env.VITE_SPOTIFY_CLIENT_ID;
    const redirectUri = 'http://localhost:3000/callback/spotify';
    const scopes = 'user-read-private user-read-email user-library-read user-top-read';
    
    const spotifyAuthUrl = `https://accounts.spotify.com/authorize?` +
        `client_id=${clientId}&` +
        `response_type=code&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `scope=${encodeURIComponent(scopes)}`;
    
    window.location.href = spotifyAuthUrl;
  };

  const handleConnect = (connectionName) => {
    if (connectionName === 'Spotify') {
        handleSpotifyConnect();
    } else {
        console.log(`Connecting to ${connectionName}`);
    }
  };

  const handleDisconnect = (connectionName) => {
    console.log(`Disconnecting from ${connectionName}`);
    // Add your disconnection logic here
  };

  return (
    <div className="connect-apps-page">
      <div className="page-content">
        <div className="page-header">
          <button onClick={() => navigate(-1)} className="back-button">
            <ArrowLeft size={24} />
          </button>
          <h2 className="page-title">Connect Applications</h2>
        </div>

        <div className="page-controls">
          <div className="search-container">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Find a connection"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
        </div>

        <div className="connections-grid">
          {filteredConnections.map((connection) => (
            <div 
                key={connection.name} 
                className="connection-card"
                onClick={() => connection.connected ? handleDisconnect(connection.name) : handleConnect(connection.name)}
            >
              <div className="connection-info">
                <img 
                  src={connection.logo} 
                  alt={`${connection.name} logo`}
                  className="connection-logo"
                  onError={(e) => {
                    e.target.src = `https://ui-avatars.com/api/?name=${connection.name}&background=random&color=fff&size=64`;
                  }}
                />
                <span className="connection-name">{connection.name}</span>
              </div>
              {connection.connected && (
                <div className="connected-indicator">Connected</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ConnectApps;