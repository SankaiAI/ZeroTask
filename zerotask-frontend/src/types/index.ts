// Types based on PRD Section 9: Data Model
export interface BriefCard {
  id: string;
  title: string;
  summary: string[];
  evidenceLinks: EvidenceLink[];
  primarySource: 'gmail' | 'slack' | 'github';
  sources: ('gmail' | 'slack' | 'github')[];
  priorityScore: number;
  createdAt: string;
  actions: CardAction[];
}

export interface EvidenceLink {
  id: string;
  source: 'gmail' | 'slack' | 'github';
  url: string;
  snippet: string;
  author?: string;
  timestamp: string;
}

export interface CardAction {
  type: 'open' | 'draft_reply' | 'follow_up' | 'snooze';
  label: string;
  enabled: boolean;
  url?: string;
}

export type PriorityLevel = 'high' | 'medium' | 'low';

export interface DailyBrief {
  id: string;
  date: string;
  cards: BriefCard[];
  stats: {
    totalCards: number;
    bySource: Record<string, number>;
    lastUpdated: string;
  };
}