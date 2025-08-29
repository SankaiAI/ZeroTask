import { useState, useEffect } from 'react';

interface AuthStatus {
  provider: string;
  connected: boolean;
  last_updated?: string;
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
  }, []);

  const handleTestConnection = async (provider: string) => {
    setTesting(provider);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/auth/${provider}/test`);
      const result = await response.json();
      
      if (response.ok) {
        alert(`✅ ${provider} connection test successful!\n${result.message}`);
      } else {
        alert(`❌ ${provider} connection test failed:\n${result.detail}`);
      }
    } catch (error) {
      alert(`❌ Network error testing ${provider} connection`);
      console.error(error);
    } finally {
      setTesting(null);
    }
  };

  const handleGmailStatus = async () => {
    setTesting('gmail');
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/gmail/status');
      const result = await response.json();
      
      if (response.ok) {
        alert(`✅ Gmail OAuth configuration found!\nClient ID: ${result.client_id}`);
      } else {
        alert(`❌ Gmail not configured:\n${result.detail}`);
      }
    } catch (error) {
      alert('❌ Network error checking Gmail status');
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
                onClick={handleGmailStatus}
                disabled={testing === 'gmail'}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {testing === 'gmail' ? 'Checking...' : 'Check Status'}
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
                  Slack
                  {authStatus.slack?.connected ? (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                      IT Configured
                    </span>
                  ) : (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      Not Configured
                    </span>
                  )}
                </h3>
                <p className="text-sm text-gray-600">Company Slack app with Socket Mode managed by IT team</p>
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
                onClick={() => handleTestConnection('slack')}
                disabled={testing === 'slack'}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {testing === 'slack' ? 'Testing...' : 'Test Connection'}
              </button>
            </div>
          </div>

          {showInstructions.slack && (
            <div className="mb-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
              <h4 className="font-semibold text-purple-900 mb-3">🛠️ IT Team Slack App Setup Instructions:</h4>
              <div className="text-sm text-purple-800 space-y-2">
                <p><strong>Configure Company-wide Slack App:</strong></p>
                <ol className="list-decimal list-inside ml-4 space-y-2 text-xs">
                  <li>Create company Slack app "ZeroTask" at <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" className="underline">api.slack.com/apps</a></li>
                  <li>Enable Socket Mode and generate App Token (xapp-) with <code className="bg-purple-100 px-1 rounded">connections:write</code> scope</li>
                  <li>Configure Bot Token Scopes: <code className="bg-purple-100 px-1 rounded">app_mentions:read</code>, <code className="bg-purple-100 px-1 rounded">channels:history</code>, <code className="bg-purple-100 px-1 rounded">chat:write</code>, <code className="bg-purple-100 px-1 rounded">im:history</code></li>
                  <li>Install app to workspace and copy Bot Token (xoxb-)</li>
                  <li>Configure environment variables:
                    <div className="ml-4 mt-1">
                      <code className="bg-purple-100 px-2 py-1 rounded block text-xs">SLACK_APP_TOKEN=xapp-your_app_token</code>
                      <code className="bg-purple-100 px-2 py-1 rounded block text-xs mt-1">SLACK_BOT_TOKEN=xoxb-your_bot_token</code>
                    </div>
                  </li>
                </ol>
                <div className="mt-3 p-2 bg-purple-100 rounded text-xs">
                  <p><strong>🔒 Security:</strong> Service account tokens managed centrally by IT team</p>
                  <p><strong>📋 Access:</strong> Bot will be added to relevant channels by IT team</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="text-sm text-gray-500">
            Socket Mode scopes: <code>app_mentions:read</code>, <code>channels:history</code>, <code>chat:write</code>, <code>im:history</code>
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