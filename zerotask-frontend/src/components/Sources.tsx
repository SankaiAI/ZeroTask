import { useState, useEffect } from 'react';

interface AuthStatus {
  provider: string;
  connected: boolean;
  last_updated?: string;
}

interface UserInfo {
  user_id?: string;
  name?: string;
  email?: string;
  avatar_url?: string;
  title?: string;
  team_id?: string;
  is_admin?: boolean;
  timezone?: string;
}

interface SlackOAuthStatus {
  configured: boolean;
  authenticated?: boolean;
  message: string;
  scopes?: string[];
  expires_at?: string;
  user_info?: UserInfo;
}

interface ValidationResult {
  status_code: number;
  message: string;
  validation: {
    configured_services: number;
    total_services: number;
    all_configured: boolean;
    services: Record<string, { configured: boolean; status: string }>;
  };
}

export function Sources() {
  const [authStatus, setAuthStatus] = useState<Record<string, AuthStatus>>({});
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [showInstructions, setShowInstructions] = useState<Record<string, boolean>>({});
  const [slackOAuthStatus, setSlackOAuthStatus] = useState<SlackOAuthStatus | null>(null);

  // Fetch IT-configured service account status
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        // Get validation status
        const validationResponse = await fetch('http://localhost:8000/api/v1/auth/validate');
        if (validationResponse.ok) {
          const validationData = await validationResponse.json();
          setValidation(validationData);
          
          // Convert validation to authStatus format for UI compatibility
          const statuses: Record<string, AuthStatus> = {};
          for (const [provider, config] of Object.entries(validationData.validation.services)) {
            const serviceConfig = config as { configured: boolean; status: string };
            statuses[provider] = {
              provider,
              connected: serviceConfig.configured
            };
          }
          setAuthStatus(statuses);
        }
      } catch (error) {
        console.error('Failed to fetch service account status:', error);
      }
    };

    fetchStatus();
    fetchSlackOAuthStatus();
  }, []);

  // Fetch Slack OAuth status including user profile
  const fetchSlackOAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/slack/oauth/status');
      if (response.ok) {
        const slackStatus = await response.json();
        setSlackOAuthStatus(slackStatus);
      }
    } catch (error) {
      console.error('Failed to fetch Slack OAuth status:', error);
    }
  };

  // Handle OAuth callback results
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Gmail OAuth callbacks
    const gmailSuccess = urlParams.get('gmail_success');
    const gmailError = urlParams.get('gmail_error');
    const userEmail = urlParams.get('email');
    
    // Slack OAuth callbacks (legacy URL-based)
    const slackSuccess = urlParams.get('slack_success');
    const slackError = urlParams.get('slack_error');
    
    if (gmailSuccess === 'true') {
      console.log(`✅ Gmail OAuth connected successfully!${userEmail ? ` Email: ${userEmail}` : ''}`);
      // Clear URL parameters and reload to update status
      window.history.replaceState({}, document.title, window.location.pathname);
      window.location.reload();
    } else if (gmailError) {
      console.error(`❌ Gmail OAuth failed: ${decodeURIComponent(gmailError)}`);
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (slackSuccess === 'true') {
      console.log(`✅ Slack OAuth connected successfully!`);
      // Clear URL parameters and reload to update status
      window.history.replaceState({}, document.title, window.location.pathname);
      window.location.reload();
    } else if (slackError) {
      console.error(`❌ Slack OAuth failed: ${decodeURIComponent(slackError)}`);
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Listen for OAuth popup messages
    const handleOAuthMessage = (event: MessageEvent) => {
      console.log('Received OAuth message:', event.data);
      
      if (event.data && event.data.type === 'oauth_success' && event.data.provider === 'slack') {
        console.log('✅ Slack OAuth connected successfully!');
        // Refresh Slack status instead of full page reload
        fetchSlackOAuthStatus();
      } else if (event.data && event.data.type === 'oauth_error' && event.data.provider === 'slack') {
        console.error(`❌ Slack OAuth failed: ${event.data.error}`);
      }
    };
    
    window.addEventListener('message', handleOAuthMessage);
    
    return () => {
      window.removeEventListener('message', handleOAuthMessage);
    };
  }, []);

  const handleTestConnection = async (provider: string) => {
    setTesting(provider);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/auth/${provider}/test`);
      const result = await response.json();
      
      if (response.ok) {
        console.log(`✅ ${provider} connection test successful! ${result.message}`);
      } else {
        console.error(`❌ ${provider} connection test failed: ${result.detail}`);
      }
    } catch (error) {
      console.error(`❌ Network error testing ${provider} connection`);
      console.error(error);
    } finally {
      setTesting(null);
    }
  };

  const handleGmailOAuth = async () => {
    setTesting('gmail');
    
    try {
      // Get current Gmail status first
      const statusResponse = await fetch('http://localhost:8000/api/v1/auth/gmail/status');
      const statusResult = await statusResponse.json();
      
      if (!statusResult.configured) {
        console.error(`❌ Gmail OAuth not configured by IT team: ${statusResult.message}`);
        setTesting(null);
        return;
      }
      
      if (statusResult.authenticated) {
        // Already authenticated - show status and offer to disconnect
        const disconnect = confirm(
          `✅ Gmail OAuth Connected!\n` +
          `Email: ${statusResult.user_email}\n` +
          `Scopes: ${statusResult.scopes?.join(', ')}\n\n` +
          `Click OK to disconnect Gmail OAuth or Cancel to keep connected.`
        );
        
        if (disconnect) {
          await handleGmailRevoke();
        }
        setTesting(null);
        return;
      }
      
      // Start OAuth flow
      const oauthResponse = await fetch('http://localhost:8000/api/v1/auth/gmail/oauth/start');
      
      if (oauthResponse.ok) {
        const oauthResult = await oauthResponse.json();
        
        console.log('=== Gmail OAuth Debug Info ===');
        console.log('Authorization URL:', oauthResult.authorization_url);
        console.log('Redirect URI:', oauthResult.redirect_uri);
        console.log('State:', oauthResult.state);
        console.log('Current Origin:', window.location.origin);
        console.log('Current URL:', window.location.href);
        
        // Parse and validate the OAuth URL
        try {
          const oauthUrl = new URL(oauthResult.authorization_url);
          console.log('=== OAuth URL Breakdown ===');
          console.log('Host:', oauthUrl.host);
          console.log('Client ID:', oauthUrl.searchParams.get('client_id'));
          console.log('Redirect URI param:', decodeURIComponent(oauthUrl.searchParams.get('redirect_uri') || ''));
          console.log('Scope:', decodeURIComponent(oauthUrl.searchParams.get('scope') || ''));
          console.log('Response Type:', oauthUrl.searchParams.get('response_type'));
        } catch (e) {
          console.error('Error parsing OAuth URL:', e);
        }
        
        // Test the OAuth URL accessibility first
        console.log('=== Testing OAuth URL Accessibility ===');
        fetch(oauthResult.authorization_url.split('?')[0], { 
          method: 'HEAD',
          mode: 'no-cors'
        })
        .then(() => console.log('OAuth endpoint is reachable'))
        .catch(err => console.error('OAuth endpoint test failed:', err));
        
        // Open OAuth URL in new window
        const authWindow = window.open(
          oauthResult.authorization_url,
          'gmail-oauth',
          'width=600,height=700,scrollbars=yes,resizable=yes'
        );
        
        console.log('Auth window opened:', authWindow !== null);
        
        // Monitor the popup window
        if (authWindow) {
          const checkClosed = setInterval(() => {
            if (authWindow.closed) {
              clearInterval(checkClosed);
              console.log('OAuth popup was closed');
            }
          }, 1000);
          
          // Try to monitor URL changes (may be blocked by CORS)
          try {
            authWindow.addEventListener('beforeunload', () => {
              console.log('OAuth window is navigating');
            });
          } catch (e) {
            console.log('Cannot monitor popup navigation (CORS blocked)');
          }
        }
        
        console.log('Gmail OAuth window opened! Complete the authorization in the new window. You will be redirected back to this page when complete. Check browser console for debug info.');
      } else {
        const errorResult = await oauthResponse.json();
        console.error(`❌ Error starting Gmail OAuth: ${errorResult.detail}`);
      }
    } catch (error) {
      console.error('❌ Network error with Gmail OAuth');
      console.error(error);
    } finally {
      setTesting(null);
    }
  };

  const handleGmailRevoke = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/gmail/oauth/revoke', {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.success) {
        console.log('✅ Gmail OAuth disconnected successfully');
        // Refresh page to update status
        window.location.reload();
      } else {
        console.error(`❌ Error disconnecting Gmail: ${result.message}`);
      }
    } catch (error) {
      console.error('❌ Network error disconnecting Gmail');
      console.error(error);
    }
  };

  const handleSlackOAuth = async () => {
    setTesting('slack-oauth');
    
    try {
      // Get current Slack OAuth status first
      const statusResponse = await fetch('http://localhost:8000/api/v1/auth/slack/oauth/status');
      const statusResult = await statusResponse.json();
      
      if (!statusResult.configured) {
        console.error(`❌ Slack OAuth not configured by IT team: ${statusResult.message}`);
        setTesting(null);
        return;
      }
      
      if (statusResult.authenticated) {
        // Already authenticated - show status and offer to disconnect
        const disconnect = confirm(
          `✅ Slack OAuth Connected!\n` +
          `Scopes: ${statusResult.scopes?.join(', ')}\n\n` +
          `Click OK to disconnect Slack OAuth or Cancel to keep connected.`
        );
        
        if (disconnect) {
          await handleSlackRevoke();
        }
        setTesting(null);
        return;
      }
      
      // Start OAuth flow
      const oauthResponse = await fetch('http://localhost:8000/api/v1/auth/slack/oauth/start');
      
      if (oauthResponse.ok) {
        const oauthResult = await oauthResponse.json();
        
        console.log('=== Slack OAuth Debug Info ===');
        console.log('Authorization URL:', oauthResult.authorization_url);
        console.log('Redirect URI:', oauthResult.redirect_uri);
        console.log('State:', oauthResult.state);
        console.log('Scopes:', oauthResult.scopes);
        
        // Open OAuth URL in new window
        const authWindow = window.open(
          oauthResult.authorization_url,
          'slack-oauth',
          'width=600,height=700,scrollbars=yes,resizable=yes'
        );
        
        if (authWindow) {
          const checkClosed = setInterval(() => {
            if (authWindow.closed) {
              clearInterval(checkClosed);
              console.log('Slack OAuth popup was closed');
            }
          }, 1000);
        }
        
        console.log('Slack OAuth window opened! Complete the authorization in the new window. You will be redirected back to this page when complete.');
      } else {
        const errorResult = await oauthResponse.json();
        console.error(`❌ Error starting Slack OAuth: ${errorResult.detail}`);
      }
    } catch (error) {
      console.error('❌ Network error with Slack OAuth');
      console.error(error);
    } finally {
      setTesting(null);
    }
  };

  const handleSlackRevoke = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/slack/oauth/revoke', {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.success) {
        console.log('✅ Slack OAuth disconnected successfully');
        // Refresh page to update status
        window.location.reload();
      } else {
        console.error(`❌ Error disconnecting Slack: ${result.message}`);
      }
    } catch (error) {
      console.error('❌ Network error disconnecting Slack');
      console.error(error);
    }
  };


  const handleGmailTest = async () => {
    setTesting('gmail');
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/gmail/test');
      const result = await response.json();
      
      if (response.ok) {
        console.log(
          `✅ Gmail API Test Successful! ` +
          `Email: ${result.email} ` +
          `Total Messages: ${result.total_messages} ` +
          `Total Threads: ${result.total_threads}`
        );
      } else {
        console.error(`❌ Gmail API Test Failed: ${result.detail}`);
      }
    } catch (error) {
      console.error('❌ Network error testing Gmail API');
      console.error(error);
    } finally {
      setTesting(null);
    }
  };

  const toggleInstructions = (provider: string) => {
    setShowInstructions(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }));
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">IT-Configured Sources</h1>
      
      {validation && (
        <div className={`mb-6 p-4 rounded-lg border ${
          validation.validation.all_configured 
            ? 'bg-green-50 border-green-200' 
            : 'bg-amber-50 border-amber-200'
        }`}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{validation.validation.all_configured ? '✅' : '⚠️'}</span>
            <h3 className={`font-semibold ${
              validation.validation.all_configured ? 'text-green-900' : 'text-amber-900'
            }`}>
              Service Account Status
            </h3>
          </div>
          <p className={`text-sm ${
            validation.validation.all_configured ? 'text-green-800' : 'text-amber-800'
          }`}>
            {validation.message}
          </p>
          <p className={`text-xs mt-1 ${
            validation.validation.all_configured ? 'text-green-700' : 'text-amber-700'
          }`}>
            {validation.validation.configured_services}/{validation.validation.total_services} services configured by IT team
          </p>
        </div>
      )}
      
      <div className="space-y-6">
        {/* Gmail */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📧</span>
              <div>
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  Gmail
                  {authStatus.gmail?.connected ? (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                      IT Configured
                    </span>
                  ) : (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      Not Configured
                    </span>
                  )}
                </h3>
                <p className="text-sm text-gray-600">Gmail OAuth credentials managed by IT team</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => toggleInstructions('gmail')}
                className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded-md hover:bg-blue-50"
              >
                {showInstructions.gmail ? 'Hide' : 'IT Setup info'}
              </button>
              <button 
                onClick={handleGmailOAuth}
                disabled={testing === 'gmail'}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {testing === 'gmail' ? 'Processing...' : 'Connect Gmail'}
              </button>
              <button 
                onClick={handleGmailTest}
                disabled={testing === 'gmail' || !authStatus.gmail?.connected}
                className="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {testing === 'gmail' ? 'Testing...' : 'Test API'}
              </button>
            </div>
          </div>

          {showInstructions.gmail && (
            <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-blue-900 mb-3">🛠️ IT Team Gmail Setup Instructions:</h4>
              <div className="text-sm text-blue-800 space-y-2">
                <p><strong>Configure Gmail OAuth for Company:</strong></p>
                <ol className="list-decimal list-inside ml-4 space-y-2 text-xs">
                  <li>Create Google Cloud Project for your organization</li>
                  <li>Enable Gmail API in the project</li>
                  <li>Configure OAuth 2.0 credentials for desktop application</li>
                  <li>Set redirect URI: <code className="bg-blue-100 px-1 rounded">http://localhost:8000/oauth2/callback</code></li>
                  <li>Configure environment variables:
                    <div className="ml-4 mt-1">
                      <code className="bg-blue-100 px-2 py-1 rounded block text-xs">GOOGLE_CLIENT_ID=your_oauth_client_id</code>
                      <code className="bg-blue-100 px-2 py-1 rounded block text-xs mt-1">GOOGLE_CLIENT_SECRET=your_oauth_client_secret</code>
                    </div>
                  </li>
                </ol>
                <div className="mt-3 p-2 bg-blue-100 rounded text-xs">
                  <p><strong>📋 Required Scopes:</strong> gmail.readonly, gmail.compose (draft only)</p>
                  <p><strong>🔒 Security:</strong> Desktop OAuth flow with localhost redirect - no public URLs needed</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="text-sm text-gray-500">
            OAuth 2.0 scopes: <code>gmail.readonly</code>, <code>gmail.compose</code> (draft only)
          </div>
        </div>

        {/* Slack */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">💬</span>
              <div>
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  Slack (Individual OAuth)
                  {slackOAuthStatus?.configured && slackOAuthStatus?.authenticated ? (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                      Connected
                    </span>
                  ) : slackOAuthStatus?.configured ? (
                    <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full">
                      Not Connected
                    </span>
                  ) : (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      Not Configured
                    </span>
                  )}
                </h3>
                <p className="text-sm text-gray-600">Individual Slack OAuth connection managed by IT team</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => toggleInstructions('slack')}
                className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded-md hover:bg-blue-50"
              >
                {showInstructions.slack ? 'Hide' : 'IT Setup info'}
              </button>
              <button 
                onClick={handleSlackOAuth}
                disabled={testing === 'slack-oauth'}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {testing === 'slack-oauth' ? 'Processing...' : (slackOAuthStatus?.authenticated ? 'Reconnect' : 'Connect Slack')}
              </button>
            </div>
          </div>

          {/* User Profile Display */}
          {slackOAuthStatus?.authenticated && slackOAuthStatus?.user_info && (
            <div className="mb-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center gap-3">
                {slackOAuthStatus.user_info.avatar_url && (
                  <img 
                    src={slackOAuthStatus.user_info.avatar_url} 
                    alt="User Avatar"
                    className="w-12 h-12 rounded-full border-2 border-green-300"
                  />
                )}
                <div>
                  <h4 className="font-semibold text-green-900">
                    {slackOAuthStatus.user_info.name || 'Unknown User'}
                  </h4>
                  {slackOAuthStatus.user_info.email && (
                    <p className="text-sm text-green-700">{slackOAuthStatus.user_info.email}</p>
                  )}
                  {slackOAuthStatus.user_info.title && (
                    <p className="text-xs text-green-600">{slackOAuthStatus.user_info.title}</p>
                  )}
                  <div className="flex items-center gap-4 mt-1">
                    <span className="text-xs text-green-600">
                      ✅ Connected to Slack
                    </span>
                    {slackOAuthStatus.user_info.is_admin && (
                      <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">Admin</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {showInstructions.slack && (
            <div className="mb-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
              <h4 className="font-semibold text-purple-900 mb-3">🛠️ IT Team Slack OAuth Setup Instructions:</h4>
              <div className="text-sm text-purple-800 space-y-2">
                <p><strong>Configure Individual Slack OAuth App:</strong></p>
                <ol className="list-decimal list-inside ml-4 space-y-2 text-xs">
                  <li>Create Slack app "ZeroTask OAuth" at <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" className="underline">api.slack.com/apps</a></li>
                  <li>Configure OAuth & Permissions with redirect URL: <code className="bg-purple-100 px-1 rounded">https://1012d16f9d68.ngrok-free.app/oauth2/slack/callback</code></li>
                  <li>Add Bot Token Scopes: <code className="bg-purple-100 px-1 rounded">channels:read</code>, <code className="bg-purple-100 px-1 rounded">chat:write</code>, <code className="bg-purple-100 px-1 rounded">users:read</code>, <code className="bg-purple-100 px-1 rounded">users:read.email</code>, <code className="bg-purple-100 px-1 rounded">channels:history</code></li>
                  <li>Copy Client ID and Client Secret from Basic Information</li>
                  <li>Configure environment variables:
                    <div className="ml-4 mt-1">
                      <code className="bg-purple-100 px-2 py-1 rounded block text-xs">SLACK_CLIENT_ID=your_oauth_client_id</code>
                      <code className="bg-purple-100 px-2 py-1 rounded block text-xs mt-1">SLACK_CLIENT_SECRET=your_oauth_client_secret</code>
                    </div>
                  </li>
                </ol>
                <div className="mt-3 p-2 bg-purple-100 rounded text-xs">
                  <p><strong>🔒 Security:</strong> Individual OAuth tokens managed per user</p>
                  <p><strong>📋 Access:</strong> Users individually authorize access to their Slack workspace</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="text-sm text-gray-500">
            OAuth scopes: <code>channels:read</code>, <code>chat:write</code>, <code>users:read</code>, <code>users:read.email</code>, <code>channels:history</code>
          </div>
        </div>

        {/* GitHub */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🔧</span>
              <div>
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  GitHub
                  {authStatus.github?.connected ? (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                      IT Configured
                    </span>
                  ) : (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      Not Configured
                    </span>
                  )}
                </h3>
                <p className="text-sm text-gray-600">Service account with organization access managed by IT team</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => toggleInstructions('github')}
                className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded-md hover:bg-blue-50"
              >
                {showInstructions.github ? 'Hide' : 'IT Setup info'}
              </button>
              <button 
                onClick={() => handleTestConnection('github')}
                disabled={testing === 'github'}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {testing === 'github' ? 'Testing...' : 'Test Connection'}
              </button>
            </div>
          </div>

          {showInstructions.github && (
            <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-blue-900 mb-3">🛠️ IT Team GitHub Service Account Setup Instructions:</h4>
              <div className="text-sm text-blue-800 space-y-2">
                <p><strong>Configure GitHub Service Account:</strong></p>
                <ol className="list-decimal list-inside ml-4 space-y-2 text-xs">
                  <li>Create dedicated service account email (e.g., "zerotask-bot@company.com")</li>
                  <li>Create GitHub user account for service account email</li>
                  <li>Invite service account to GitHub organization with appropriate team membership</li>
                  <li>Grant repository access to relevant repositories that need monitoring</li>
                  <li>Generate Personal Access Token with required scopes:
                    <div className="ml-4 mt-1">
                      <code className="bg-blue-100 px-1 rounded">repo</code> - Full repository access<br/>
                      <code className="bg-blue-100 px-1 rounded">read:user</code> - Read user profile<br/>
                      <code className="bg-blue-100 px-1 rounded">notifications</code> - Access notifications
                    </div>
                  </li>
                  <li>Configure environment variable:
                    <div className="ml-4 mt-1">
                      <code className="bg-blue-100 px-2 py-1 rounded block text-xs">GITHUB_TOKEN=ghp_your_service_account_token</code>
                    </div>
                  </li>
                </ol>
                <div className="mt-3 p-2 bg-blue-100 rounded text-xs">
                  <p><strong>🔒 Security:</strong> Service account PAT managed centrally with 90-day rotation</p>
                  <p><strong>📋 Access:</strong> Repository permissions configured by IT team</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="text-sm text-gray-500">
            Required scopes: <code>repo</code>, <code>read:user</code>, <code>notifications</code>
          </div>
        </div>
      </div>
    </div>
  );
}