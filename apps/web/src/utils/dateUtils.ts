/**
 * Format a date/time string to local time
 * Ensures proper timezone handling for timestamps from the API
 */
export function formatDateTime(dateTimeString: string | Date): string {
  const date = typeof dateTimeString === 'string' ? new Date(dateTimeString) : dateTimeString;

  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format a date string (without time)
 * Handles date-only strings (YYYY-MM-DD) correctly without timezone conversion
 */
export function formatDate(dateString: string | Date): string {
  if (typeof dateString === 'string' && dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
    // Date-only string (YYYY-MM-DD) - parse as local date, not UTC
    const [year, month, day] = dateString.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Parse a date string (YYYY-MM-DD) as a local date, avoiding timezone issues
 */
export function parseLocalDate(dateString: string): Date {
  const [year, month, day] = dateString.split('-').map(Number);
  return new Date(year, month - 1, day);
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateTimeString: string | Date): string {
  const date = typeof dateTimeString === 'string' ? new Date(dateTimeString) : dateTimeString;
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  return formatDateTime(date);
}
