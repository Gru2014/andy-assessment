import React from 'react';

export type HeadingLevel = 1 | 2 | 3 | 4 | 5 | 6;

export interface HeadingProps {
  level?: HeadingLevel;
  children: React.ReactNode;
  className?: string;
}

const levelClasses: Record<HeadingLevel, string> = {
  1: 'text-3xl font-bold',
  2: 'text-2xl font-bold',
  3: 'text-xl font-semibold',
  4: 'text-lg font-semibold',
  5: 'text-base font-semibold',
  6: 'text-sm font-semibold',
};

export const Heading: React.FC<HeadingProps> = ({
  level = 2,
  children,
  className = '',
}) => {
  const Tag = `h${level}` as keyof React.JSX.IntrinsicElements;
  const baseClasses = 'text-gray-800';
  const levelClass = levelClasses[level];

  return (
    <Tag className={`${baseClasses} ${levelClass} ${className}`}>
      {children}
    </Tag>
  );
};

