import { User } from 'lucide-react';

interface AvatarProps {
  src?: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
};

const iconSizes = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
};

export function Avatar({ src, alt = 'User avatar', size = 'md' }: AvatarProps) {
  return (
    <div
      className={`${sizeClasses[size]} rounded-lg overflow-hidden flex-shrink-0 bg-blue-100 flex items-center justify-center`}
    >
      {src ? (
        <img src={src} alt={alt} className="w-full h-full object-cover" />
      ) : (
        <User className={`${iconSizes[size]} text-blue-600`} />
      )}
    </div>
  );
}
