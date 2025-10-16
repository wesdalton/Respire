import { useState, useEffect } from 'react';

interface MoodEntryProps {
  onSubmit: (rating: number, notes: string) => void;
  initialRating?: number;
  initialNotes?: string;
  isEditing?: boolean;
}

const MOOD_EMOJIS = ['😢', '😔', '😟', '😕', '😐', '🙂', '😊', '😄', '🥳', '🤩'];

export default function MoodEntry({ onSubmit, initialRating, initialNotes, isEditing }: MoodEntryProps) {
  const [selectedRating, setSelectedRating] = useState<number | null>(initialRating ?? null);
  const [notes, setNotes] = useState(initialNotes ?? '');

  // Update state when initial values change (for editing)
  useEffect(() => {
    if (initialRating !== undefined) {
      setSelectedRating(initialRating);
    }
    if (initialNotes !== undefined) {
      setNotes(initialNotes);
    }
  }, [initialRating, initialNotes]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedRating !== null) {
      onSubmit(selectedRating, notes);
      // Reset form
      setSelectedRating(null);
      setNotes('');
    }
  };

  // Check if form has changed when editing
  const hasChanges = isEditing
    ? selectedRating !== initialRating || notes !== (initialNotes ?? '')
    : true;

  const isSubmitDisabled = selectedRating === null || (isEditing && !hasChanges);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">
        {isEditing ? 'Edit Mood Rating' : 'How are you feeling today?'}
      </h2>

      <form onSubmit={handleSubmit}>
        {/* Emoji Rating Buttons */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select your mood (1-10)
          </label>
          <div className="grid grid-cols-5 sm:grid-cols-10 gap-2">
            {MOOD_EMOJIS.map((emoji, index) => {
              const rating = index + 1;
              const isSelected = selectedRating === rating;

              return (
                <button
                  key={rating}
                  type="button"
                  onClick={() => setSelectedRating(rating)}
                  className={`
                    text-4xl p-3 rounded-lg transition-all duration-200
                    hover:bg-blue-50 hover:scale-105
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    ${isSelected ? 'bg-blue-100 scale-110 ring-2 ring-blue-500' : 'bg-gray-50'}
                  `}
                  title={`Rating ${rating}`}
                  aria-label={`Mood rating ${rating}`}
                >
                  {emoji}
                </button>
              );
            })}
          </div>
          {selectedRating !== null && (
            <p className="mt-3 text-sm text-gray-600">
              Selected rating: <span className="font-semibold">{selectedRating}/10</span>
            </p>
          )}
        </div>

        {/* Notes Textarea */}
        <div className="mb-6">
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
            Notes (optional)
          </label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any thoughts or context about your mood..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitDisabled}
          className={`
            w-full py-3 px-6 rounded-lg font-medium text-white transition-all duration-200
            ${!isSubmitDisabled
              ? 'bg-blue-600 hover:bg-blue-700 active:scale-95 shadow-md hover:shadow-lg'
              : 'bg-gray-300 cursor-not-allowed'
            }
          `}
        >
          {isEditing ? 'Update Mood Rating' : 'Save Mood Rating'}
        </button>
      </form>
    </div>
  );
}
