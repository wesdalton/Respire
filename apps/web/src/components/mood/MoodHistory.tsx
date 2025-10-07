import { Edit2, Trash2 } from 'lucide-react';
import type { MoodRating } from '../../types';

interface MoodHistoryProps {
  moods: MoodRating[];
  onEdit?: (mood: MoodRating) => void;
  onDelete?: (moodDate: string) => void;
}

const MOOD_EMOJIS = ['😢', '😟', '😐', '🙂', '😊', '😃', '🤗', '😄', '🥳', '🤩'];

export default function MoodHistory({ moods, onEdit, onDelete }: MoodHistoryProps) {
  const formatDate = (dateString: string) => {
    // Parse the date string as a local date (YYYY-MM-DD format)
    const [year, month, day] = dateString.split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed

    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to midnight for accurate comparison

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    // Normalize the date to midnight for comparison
    const normalizedDate = new Date(date);
    normalizedDate.setHours(0, 0, 0, 0);

    // Check if it's today
    if (normalizedDate.getTime() === today.getTime()) {
      return 'Today';
    }

    // Check if it's yesterday
    if (normalizedDate.getTime() === yesterday.getTime()) {
      return 'Yesterday';
    }

    // Otherwise, format as readable date
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
    });
  };

  const getEmoji = (rating: number) => {
    // Rating is 1-10, array is 0-indexed
    return MOOD_EMOJIS[rating - 1] || '😐';
  };

  if (moods.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">📊</div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">No mood ratings yet</h3>
        <p className="text-gray-600">Start tracking your mood to see your history here.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Mood History</h2>

      <div className="space-y-4">
        {moods.map((mood) => (
          <div
            key={mood.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-start justify-between gap-4">
              {/* Emoji and Rating */}
              <div className="flex items-center gap-4">
                <div className="text-5xl flex-shrink-0">
                  {getEmoji(mood.rating)}
                </div>

                <div className="flex-1 min-w-0">
                  {/* Date and Rating */}
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-lg font-semibold text-gray-800">
                      {formatDate(mood.date)}
                    </span>
                    <span className="text-sm font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
                      {mood.rating}/10
                    </span>
                  </div>

                  {/* Notes */}
                  {mood.notes && (
                    <p className="text-gray-700 text-sm mt-2 break-words">
                      {mood.notes}
                    </p>
                  )}

                  {/* Timestamp */}
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(mood.created_at).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                      hour12: true
                    })}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-2 flex-shrink-0">
                {onEdit && (
                  <button
                    onClick={() => onEdit(mood)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                    title="Edit mood rating"
                    aria-label="Edit mood rating"
                  >
                    <Edit2 size={18} />
                  </button>
                )}

                {onDelete && (
                  <button
                    onClick={() => onDelete(mood.date)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
                    title="Delete mood rating"
                    aria-label="Delete mood rating"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
