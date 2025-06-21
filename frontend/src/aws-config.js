const awsConfig = {
  Auth: {
    Cognito: {
      region: 'us-east-1', // Your AWS region
      userPoolId: 'us-east-1_RwbDs7naF', // Your User Pool ID
      userPoolClientId: '42sbpug2u49vp7o3h7c7k9bcac', // Your App Client ID
      loginWith: {
        oauth: {
          domain: 'https://us-east-1rwbds7naf.auth.us-east-1.amazoncognito.com',
          scopes: ['openid', 'email', 'profile'],
          redirectSignIn: ['http://localhost:5173/'],
          redirectSignOut: ['http://localhost:5173/'],
          responseType: 'code'
        }
      }
    }
  }
};

export default awsConfig;