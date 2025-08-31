'use client';

import { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { DailyBrief } from '@/components/DailyBrief';
import { Sources } from '@/components/Sources';
import { Preferences } from '@/components/Preferences';
import { Settings } from '@/components/Settings';

export default function Home() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [brief, setBrief] = useState({
    id: `daily-brief-${new Date().toISOString().split('T')[0]}`,
    date: new Date().toISOString().split('T')[0],
    cards: [],
    stats: {
      totalCards: 0,
      bySource: {},
      lastUpdated: new Date().toISOString()
    }
  });
  const [loading, setLoading] = useState(false);

  // Function to fetch Slack daily brief and convert to cards
  const fetchSlackDailyBrief = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/slack/daily-brief');
      if (response.ok) {
        const slackData = await response.json();
        
        // Create Slack cards from the data
        const slackCards = [];
        
        // Card 1: Workspace Overview
        slackCards.push({
          id: `slack-overview-${Date.now()}`,
          title: `📊 Slack Workspace Summary`,
          summary: [`Connected to ${slackData.stats.total_channels} channels. ${slackData.stats.messages_today} messages today, ${slackData.stats.mentions_today} mentions.`],
          evidenceLinks: [],
          primarySource: 'slack',
          sources: ['slack'],
          priorityScore: 7,
          createdAt: slackData.generated_at,
          actions: [
            {
              type: 'open',
              label: 'Open Slack',
              enabled: true,
              url: 'https://app.slack.com'
            }
          ]
        });

        // Card 2: Channel List (if any)
        if (slackData.channels && slackData.channels.length > 0) {
          slackCards.push({
            id: `slack-channels-${Date.now()}`,
            title: `📁 Active Channels`,
            summary: [`You have access to ${slackData.channels.length} channels: ${slackData.channels.map(ch => `#${ch.name}`).join(', ')}`],
            evidenceLinks: [],
            primarySource: 'slack',
            sources: ['slack'],
            priorityScore: 5,
            createdAt: slackData.generated_at,
            actions: [
              {
                type: 'open',
                label: 'View Channels',
                enabled: true,
                url: 'https://app.slack.com'
              }
            ]
          });
        }

        // Card 3: Recent Messages (if any)
        if (slackData.recent_messages && slackData.recent_messages.length > 0) {
          slackCards.push({
            id: `slack-messages-${Date.now()}`,
            title: `💬 Recent Activity`,
            summary: [`${slackData.recent_messages.length} recent messages across your channels`],
            evidenceLinks: [],
            primarySource: 'slack',
            sources: ['slack'],
            priorityScore: 8,
            createdAt: slackData.generated_at,
            actions: [
              {
                type: 'open',
                label: 'View Messages',
                enabled: true,
                url: 'https://app.slack.com'
              }
            ]
          });
        }

        // Card 4: Mentions (if any)
        if (slackData.mentions && slackData.mentions.length > 0) {
          slackCards.push({
            id: `slack-mentions-${Date.now()}`,
            title: `🔔 You were mentioned`,
            summary: [`${slackData.mentions.length} messages mention you today`],
            evidenceLinks: [],
            primarySource: 'slack',
            sources: ['slack'],
            priorityScore: 9,
            createdAt: slackData.generated_at,
            actions: [
              {
                type: 'open',
                label: 'View Mentions',
                enabled: true,
                url: 'https://app.slack.com'
              }
            ]
          });
        }

        // Update brief with Slack cards
        const updatedBrief = {
          id: `daily-brief-${new Date().toISOString().split('T')[0]}`,
          date: new Date().toISOString().split('T')[0],
          cards: slackCards,
          stats: {
            totalCards: slackCards.length,
            bySource: {
              slack: slackCards.length
            },
            lastUpdated: new Date().toISOString()
          }
        };

        setBrief(updatedBrief);
        console.log('✅ Slack daily brief loaded:', updatedBrief);
      } else {
        console.error('❌ Failed to fetch Slack data:', response.status);
        // Keep showing empty state if Slack fetch fails
      }
    } catch (error) {
      console.error('❌ Error fetching Slack daily brief:', error);
      // Keep showing empty state if there's an error
    } finally {
      setLoading(false);
    }
  };

  // Load Slack data on component mount and when dashboard is viewed
  useEffect(() => {
    if (currentView === 'dashboard') {
      fetchSlackDailyBrief();
    }
  }, [currentView]);

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
    console.log('Refreshing daily brief...');
    fetchSlackDailyBrief();
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <DailyBrief 
            brief={brief}
            onCardAction={handleCardAction}
            onRefresh={handleRefresh}
            loading={loading}
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
