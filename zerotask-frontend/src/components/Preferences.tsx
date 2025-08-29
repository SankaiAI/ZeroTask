export function Preferences() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Preferences</h1>
      
      <div className="space-y-8">
        {/* LLM Provider */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">LLM Provider</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <input type="radio" id="ollama" name="llm" defaultChecked className="text-blue-600" />
              <label htmlFor="ollama" className="font-medium">Ollama (Local)</label>
            </div>
            <div className="flex items-center gap-3">
              <input type="radio" id="openai" name="llm" className="text-blue-600" />
              <label htmlFor="openai" className="font-medium">OpenAI (BYOK)</label>
            </div>
            <div className="flex items-center gap-3">
              <input type="radio" id="anthropic" name="llm" className="text-blue-600" />
              <label htmlFor="anthropic" className="font-medium">Anthropic (BYOK)</label>
            </div>
          </div>
        </div>

        {/* Daily Brief Settings */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Brief</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Brief Time
              </label>
              <input 
                type="time" 
                defaultValue="09:00"
                className="block w-32 px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div className="flex items-center gap-3">
              <input type="checkbox" id="mentions" defaultChecked className="text-blue-600" />
              <label htmlFor="mentions" className="text-sm font-medium text-gray-700">
                Only show @mentions and assigned items
              </label>
            </div>
          </div>
        </div>

        {/* Source Filters */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Filters</h3>
          
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Gmail Labels</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <input type="checkbox" id="inbox" defaultChecked className="text-blue-600" />
                  <label htmlFor="inbox" className="text-sm">INBOX</label>
                </div>
                <div className="flex items-center gap-3">
                  <input type="checkbox" id="starred" className="text-blue-600" />
                  <label htmlFor="starred" className="text-sm">STARRED</label>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Slack Channels</h4>
              <div className="text-sm text-gray-600">Configure after connecting Slack</div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">GitHub Repositories</h4>
              <div className="text-sm text-gray-600">Configure after connecting GitHub</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}