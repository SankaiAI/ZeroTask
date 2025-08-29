import { useState } from 'react';
import { BriefCard as BriefCardType } from '@/types';
import { cn, getPriorityLevel, getPriorityColor, getSourceIcon } from '@/lib/utils';

interface BriefCardProps {
  card: BriefCardType;
  onAction: (cardId: string, action: string) => void;
}

export function BriefCard({ card, onAction }: BriefCardProps) {
  const [showSources, setShowSources] = useState(false);
  const priorityLevel = getPriorityLevel(card.priorityScore);
  const priorityColorClass = getPriorityColor(priorityLevel);

  return (
    <article 
      className={cn(
        "bg-white rounded-lg shadow-sm border border-gray-300 p-5 hover:shadow-md transition-shadow",
        "border-l-4",
        priorityColorClass
      )}
      aria-labelledby={`card-title-${card.id}`}
    >
      {/* Header Section */}
      <div className="mb-4">
        <h2 
          id={`card-title-${card.id}`}
          className="text-base font-semibold text-gray-900 leading-tight mb-2"
        >
          {card.title}
        </h2>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            {card.sources.map((source, index) => (
              <span key={index} title={source}>
                {getSourceIcon(source)}
              </span>
            ))}
          </span>
          <span>•</span>
          <span>Priority: {priorityLevel}</span>
        </div>
      </div>

      {/* Summary Section */}
      <div className="mb-4 space-y-2">
        {card.summary.map((bullet, index) => (
          <div key={index} className="text-sm text-gray-700 leading-relaxed">
            <span className="inline-block w-2 h-2 bg-gray-400 rounded-full mr-2 flex-shrink-0 mt-2"></span>
            <span dangerouslySetInnerHTML={{ __html: bullet }} />
          </div>
        ))}
      </div>

      {/* Sources Section (Expandable) */}
      {card.evidenceLinks.length > 0 && (
        <div className="mb-4">
          <button
            onClick={() => setShowSources(!showSources)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            aria-expanded={showSources}
          >
            {showSources ? '▼' : '▶'} View sources ({card.evidenceLinks.length})
          </button>
          
          {showSources && (
            <div className="mt-3 space-y-2 pl-4 border-l-2 border-gray-200">
              {card.evidenceLinks.map((link) => (
                <div key={link.id} className="text-sm">
                  <div className="flex items-center gap-2 mb-1">
                    <span>{getSourceIcon(link.source)}</span>
                    <span className="text-gray-600">{link.author}</span>
                    <span className="text-gray-400">•</span>
                    <span className="text-gray-400">
                      {new Date(link.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-gray-600 italic pl-6">"{link.snippet}"</p>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700 text-xs pl-6"
                  >
                    Open source →
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        {card.actions.map((action) => {
          const isPrimary = action.type === 'open';
          const isSecondary = ['draft_reply', 'follow_up'].includes(action.type);
          const isGhost = action.type === 'snooze';

          return (
            <button
              key={action.type}
              onClick={() => onAction(card.id, action.type)}
              disabled={!action.enabled}
              className={cn(
                "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                "focus:outline-none focus:ring-2 focus:ring-offset-2",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                isPrimary && [
                  "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
                  "disabled:hover:bg-blue-600"
                ],
                isSecondary && [
                  "border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400",
                  "focus:ring-gray-500"
                ],
                isGhost && [
                  "text-gray-600 hover:text-gray-800 hover:bg-gray-100",
                  "focus:ring-gray-400"
                ]
              )}
              aria-label={`${action.label} for ${card.title}`}
            >
              {action.type === 'snooze' && '⏰ '}
              {action.label}
            </button>
          );
        })}
      </div>
    </article>
  );
}