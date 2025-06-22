import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { fetchAuthSession } from 'aws-amplify/auth';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const [hasProcessed, setHasProcessed] = useState(false);
  
  useEffect(() => {
    if (hasProcessed) return;
    setHasProcessed(true);

    const handleCallback = async () => {
      const error = searchParams.get('error');
      const code = searchParams.get('code');
      const service = location.pathname.split('/')[2];
      
      if (error || !code) {
        window.location.href = 'http://localhost:5173/connect-apps';
        return;
      }
      
      try {
        const session = await fetchAuthSession();
        const userToken = session.tokens.accessToken.toString();
        
        await fetch(`http://localhost:5050/api/callback/${service}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userToken}`
          },
          body: JSON.stringify({ code })
        });
        
        window.location.href = 'http://localhost:5173/connect-apps';
      } catch (error) {
        window.location.href = 'http://localhost:5173/connect-apps?error=callback_failed';
      }
    };
    
    handleCallback();
  }, [searchParams, navigate, location]);
  
  return <div>Connecting...</div>;
};

export default OAuthCallback;