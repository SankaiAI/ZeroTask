import { DailyBrief } from '@/types';

// Mock data following PRD specifications (Section 9: Data Model)
export const mockDailyBrief: DailyBrief = {
  id: 'brief-2025-08-29',
  date: '2025-08-29',
  stats: {
    totalCards: 4,
    bySource: {
      gmail: 2,
      slack: 1, 
      github: 1
    },
    lastUpdated: '2025-08-29T09:00:00Z'
  },
  cards: [
    {
      id: 'card-1',
      title: 'Q4 Planning Discussion - Product Team',
      summary: [
        'Sarah mentioned <em>"we need to prioritize the user onboarding flow"</em> for Q4 roadmap',
        'Three key features identified: dashboard redesign, mobile app, and analytics',
        'Decision needed on resource allocation between frontend and backend teams',
        'Follow-up meeting scheduled for Friday to finalize scope'
      ],
      evidenceLinks: [
        {
          id: 'evidence-1',
          source: 'gmail',
          url: 'https://mail.google.com/mail/u/0/#inbox/thread-123',
          snippet: 'Hi team, I think we need to prioritize the user onboarding flow for Q4. Based on user feedback...',
          author: 'sarah@company.com',
          timestamp: '2025-08-29T08:30:00Z'
        },
        {
          id: 'evidence-2', 
          source: 'slack',
          url: 'https://company.slack.com/archives/C123/p1234567890',
          snippet: '@channel - following up on Sarah\'s email, here are the three features we discussed...',
          author: 'john.doe',
          timestamp: '2025-08-29T08:45:00Z'
        }
      ],
      primarySource: 'gmail',
      sources: ['gmail', 'slack'],
      priorityScore: 9,
      createdAt: '2025-08-29T09:00:00Z',
      actions: [
        { type: 'open', label: 'Open', enabled: true, url: 'https://mail.google.com/mail/u/0/#inbox/thread-123' },
        { type: 'draft_reply', label: 'Draft Reply', enabled: true },
        { type: 'follow_up', label: 'Follow-Up', enabled: true },
        { type: 'snooze', label: 'Snooze', enabled: true }
      ]
    },
    {
      id: 'card-2',
      title: 'API Rate Limit Issues - #infrastructure',
      summary: [
        'Multiple reports of 429 errors in production API calls',
        'DevOps team investigating <em>"unusual spike in traffic from mobile clients"</em>',
        'Temporary rate limit increase deployed as hotfix',
        'Root cause analysis needed to prevent recurrence'
      ],
      evidenceLinks: [
        {
          id: 'evidence-3',
          source: 'slack',
          url: 'https://company.slack.com/archives/C456/p1234567891',
          snippet: 'Seeing multiple 429 errors in our production logs. Mobile traffic looks unusual...',
          author: 'devops.jane',
          timestamp: '2025-08-29T07:15:00Z'
        }
      ],
      primarySource: 'slack',
      sources: ['slack'],
      priorityScore: 8,
      createdAt: '2025-08-29T09:00:00Z',
      actions: [
        { type: 'open', label: 'Open', enabled: true, url: 'https://company.slack.com/archives/C456/p1234567891' },
        { type: 'follow_up', label: 'Follow-Up', enabled: true },
        { type: 'snooze', label: 'Snooze', enabled: true }
      ]
    },
    {
      id: 'card-3',
      title: 'Pull Request Review: Authentication Refactor',
      summary: [
        'Large PR updating OAuth2 implementation with security improvements',
        'Breaking changes require <em>"careful review of integration tests"</em>',
        'PR has been open for 3 days and blocks other authentication work',
        'Two approvals received, waiting for security team review'
      ],
      evidenceLinks: [
        {
          id: 'evidence-4',
          source: 'github',
          url: 'https://github.com/company/app/pull/456',
          snippet: 'This PR refactors our OAuth2 implementation to address security vulnerabilities...',
          author: 'alex.dev',
          timestamp: '2025-08-26T14:30:00Z'
        },
        {
          id: 'evidence-5',
          source: 'gmail',
          url: 'https://mail.google.com/mail/u/0/#inbox/thread-456',
          snippet: 'Hi security team, could you please review PR #456? It\'s blocking our sprint...',
          author: 'tech.lead@company.com',
          timestamp: '2025-08-28T16:00:00Z'
        }
      ],
      primarySource: 'github',
      sources: ['github', 'gmail'],
      priorityScore: 7,
      createdAt: '2025-08-29T09:00:00Z',
      actions: [
        { type: 'open', label: 'Open', enabled: true, url: 'https://github.com/company/app/pull/456' },
        { type: 'follow_up', label: 'Follow-Up', enabled: true },
        { type: 'snooze', label: 'Snooze', enabled: true }
      ]
    },
    {
      id: 'card-4',
      title: 'Weekly Team Sync Notes',
      summary: [
        'Sprint retrospective identified process improvements for code reviews',
        'New team member onboarding scheduled for next week',
        'Updated coding standards document needs team review by Friday'
      ],
      evidenceLinks: [
        {
          id: 'evidence-6',
          source: 'slack',
          url: 'https://company.slack.com/archives/C789/p1234567892',
          snippet: 'Thanks everyone for the productive retro. Here are the action items...',
          author: 'scrum.master',
          timestamp: '2025-08-28T17:00:00Z'
        }
      ],
      primarySource: 'slack',
      sources: ['slack'],
      priorityScore: 4,
      createdAt: '2025-08-29T09:00:00Z',
      actions: [
        { type: 'open', label: 'Open', enabled: true, url: 'https://company.slack.com/archives/C789/p1234567892' },
        { type: 'follow_up', label: 'Follow-Up', enabled: true },
        { type: 'snooze', label: 'Snooze', enabled: true }
      ]
    }
  ]
};