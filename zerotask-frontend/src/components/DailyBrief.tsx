import { DailyBrief as DailyBriefType } from '@/types';
import { BriefCard } from './BriefCard';
import { formatDate } from '@/lib/utils';

interface DailyBriefProps {
  brief: DailyBriefType;
  onCardAction: (cardId: string, action: string) => void;
  onRefresh: () => void;
}

export function DailyBrief({ brief, onCardAction, onRefresh }: DailyBriefProps) {
  const { totalCards, bySource, lastUpdated } = brief.stats;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              Daily Brief
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              {formatDate(brief.date)}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              {totalCards} cards requiring attention
            </div>
            <button
              onClick={onRefresh}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              ↻ Refresh
            </button>
          </div>
        </div>
        
        {/* Stats Bar */}
        {Object.keys(bySource).length > 0 && (
          <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
            {Object.entries(bySource).map(([source, count]) => (
              <div key={source} className="flex items-center gap-1">
                <span>{source === 'gmail' ? '📧' : source === 'slack' ? '💬' : '🔧'}</span>
                <span>{count} {source}</span>
              </div>
            ))}
            <div className="ml-auto">
              Last updated: {new Date(lastUpdated).toLocaleTimeString('en-US', { 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div>
        {brief.cards.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">🎉</div>
            <h2 className="text-lg font-medium text-gray-900 mb-2">
              All caught up!
            </h2>
            <p className="text-gray-600">
              No cards require your attention right now. Check back later or click refresh.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {brief.cards
              .sort((a, b) => b.priorityScore - a.priorityScore)
              .map((card) => (
                <BriefCard
                  key={card.id}
                  card={card}
                  onAction={onCardAction}
                />
              ))}
          </div>
        )}
      </div>
    </div>
  );
}