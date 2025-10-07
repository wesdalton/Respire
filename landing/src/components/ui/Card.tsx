import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface CardProps {
  className?: string;
  hover?: boolean;
  glass?: boolean;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  className,
  hover = false,
  glass = false,
  children
}) => {
  const baseClasses = 'rounded-xl p-6 border';

  const variants = {
    default: 'bg-white border-gray-200 shadow-lg',
    glass: 'bg-white/80 backdrop-blur-sm border-white/20 shadow-lg',
  };

  const Component = hover ? motion.div : 'div';

  const motionProps = hover ? {
    whileHover: { y: -4, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' },
    transition: { duration: 0.2 }
  } : {};

  return (
    <Component
      className={clsx(
        baseClasses,
        glass ? variants.glass : variants.default,
        className
      )}
      {...motionProps}
    >
      {children}
    </Component>
  );
};