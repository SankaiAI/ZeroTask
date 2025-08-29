export function Settings() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Settings</h1>
      
      <div className="space-y-6">
        {/* Data Management */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Management</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Export Data</h4>
              <p className="text-sm text-gray-600 mb-3">
                Export your settings and data in portable format
              </p>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                Export Settings
              </button>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Reset & Wipe</h4>
              <p className="text-sm text-gray-600 mb-3">
                Permanently delete all local data and reset to defaults
              </p>
              <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">
                Reset & Wipe Data
              </button>
            </div>
          </div>
        </div>

        {/* Privacy & Security */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Privacy & Security</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Debug Logging</div>
                <div className="text-sm text-gray-600">Enable detailed logs for troubleshooting</div>
              </div>
              <input type="checkbox" className="text-blue-600" />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Local-First Mode</div>
                <div className="text-sm text-gray-600">All data stays on your device</div>
              </div>
              <input type="checkbox" defaultChecked disabled className="text-green-600" />
            </div>
          </div>
        </div>

        {/* About */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">About</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <div>ZeroTask v0.1.0</div>
            <div>Privacy-first daily brief for Gmail, Slack & GitHub</div>
            <div>Running locally on localhost:3001</div>
          </div>
        </div>
      </div>
    </div>
  );
}