'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { DailyBrief } from '@/components/DailyBrief';
import { Sources } from '@/components/Sources';
import { Preferences } from '@/components/Preferences';
import { Settings } from '@/components/Settings';
import { mockDailyBrief } from '@/lib/mockData';

export default function Home() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [brief, setBrief] = useState(mockDailyBrief);

  const handleCardAction = (cardId: string, action: string) => {
    console.log(`Action: ${action} on card: ${cardId}`);
    
    // Handle different actions based on PRD Section 5.3 (Actions MVP)
    switch (action) {
      case 'open':
        // Open source item in browser/native app
        const card = brief.cards.find(c => c.id === cardId);
        const actionData = card?.actions.find(a => a.type === 'open');
        if (actionData?.url) {
          window.open(actionData.url, '_blank');
        }
        break;
        
      case 'draft_reply':
        // Create Gmail draft reply (PRD: prefill body; user must review & send in Gmail)
        alert('Draft Reply: This would open Gmail with a prefilled draft reply.');
        break;
        
      case 'follow_up':
        // Add Follow-Up: lightweight local todo with due-date
        alert('Follow-Up: This would create a local todo item for tomorrow\'s brief.');
        break;
        
      case 'snooze':
        // Snooze to tomorrow
        setBrief(prev => ({
          ...prev,
          cards: prev.cards.filter(c => c.id !== cardId),
          stats: {
            ...prev.stats,
            totalCards: prev.stats.totalCards - 1
          }
        }));
        break;
    }
  };

  const handleRefresh = () => {
    // Simulate refresh - in real app, this would fetch new data from API
    setBrief({ ...mockDailyBrief });
    console.log('Refreshing daily brief...');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <DailyBrief 
            brief={brief}
            onCardAction={handleCardAction}
            onRefresh={handleRefresh}
          />
        );
      case 'sources':
        return <Sources />;
      case 'preferences':
        return <Preferences />;
      case 'settings':
        return <Settings />;
      default:
        return (
          <div className="p-6">
            <h1 className="text-2xl font-semibold text-gray-900">View not found</h1>
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        currentView={currentView}
        onViewChange={setCurrentView}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <main className="flex-1 overflow-auto">
        {renderCurrentView()}
      </main>
    </div>
  );
}
