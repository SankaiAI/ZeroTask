import { useState } from 'react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  currentView: string;
  onViewChange: (view: string) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

interface NavItem {
  id: string;
  label: string;
  icon: string;
  description: string;
}

const navItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Daily Brief',
    icon: '📊',
    description: 'View your daily summary cards'
  },
  {
    id: 'sources',
    label: 'Sources',
    icon: '🔌',
    description: 'Connect Gmail, Slack, GitHub'
  },
  {
    id: 'preferences',
    label: 'Preferences',
    icon: '⚙️',
    description: 'LLM provider, timing, filters'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: '🔧',
    description: 'Advanced configuration'
  }
];

export function Sidebar({ currentView, onViewChange, isCollapsed = false, onToggleCollapse }: SidebarProps) {
  return (
    <aside 
      className={cn(
        "bg-white border-r border-gray-200 transition-all duration-300 flex flex-col",
        isCollapsed ? "w-16" : "w-64"
      )}
      role="navigation"
      aria-label="Main navigation"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        {!isCollapsed ? (
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">ZeroTask</h1>
              <p className="text-xs text-gray-500 mt-0.5">Local Daily Brief</p>
            </div>
            <button
              onClick={onToggleCollapse}
              className="p-1 hover:bg-gray-100 rounded-md"
              aria-label="Collapse sidebar"
            >
              ◀
            </button>
          </div>
        ) : (
          <div className="flex justify-center">
            <button
              onClick={onToggleCollapse}
              className="p-2 hover:bg-gray-100 rounded-md"
              aria-label="Expand sidebar"
            >
              ▶
            </button>
          </div>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 p-2">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = currentView === item.id;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onViewChange(item.id)}
                  className={cn(
                    "w-full text-left p-3 rounded-lg transition-colors",
                    "flex items-center gap-3",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
                    isActive 
                      ? "bg-blue-50 text-blue-700 border-l-3 border-blue-600" 
                      : "text-gray-700 hover:bg-gray-100"
                  )}
                  aria-current={isActive ? 'page' : undefined}
                  title={isCollapsed ? item.label : undefined}
                >
                  <span className="text-lg flex-shrink-0" role="img" aria-label={item.label}>
                    {item.icon}
                  </span>
                  {!isCollapsed && (
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{item.label}</div>
                      <div className="text-xs text-gray-500 truncate">{item.description}</div>
                    </div>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Status Section */}
      <div className="p-2 border-t border-gray-200">
        {!isCollapsed ? (
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">Connected</span>
            </div>
            <div className="text-xs text-gray-500">
              Last sync: {new Date().toLocaleTimeString('en-US', { 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div 
              className="w-3 h-3 bg-green-500 rounded-full"
              title="System status: Connected"
            />
          </div>
        )}
      </div>
    </aside>
  );
}