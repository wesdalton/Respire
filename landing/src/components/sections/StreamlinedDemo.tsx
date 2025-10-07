import React from 'react';
import { FluidScrollDemo } from '../interactive/FluidScrollDemo';

export const StreamlinedDemo: React.FC = () => {
  return (
    <section id="demo" className="relative">
      {/* Minimal height, much closer to hero */}
      <FluidScrollDemo />
    </section>
  );
};