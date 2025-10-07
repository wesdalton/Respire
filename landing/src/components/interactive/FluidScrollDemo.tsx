import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { EnhancedDashboardDemo } from './EnhancedDashboardDemo';

export const FluidScrollDemo: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });

  // Much more fluid transforms - demo starts visible and scales/moves smoothly
  const demoScale = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0.7, 1, 1.05, 1.1]);
  const demoY = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [100, 0, -20, -50]);
  const demoOpacity = useTransform(scrollYProgress, [0, 0.1, 0.9, 1], [0.3, 1, 1, 0.8]);
  const demoRotateX = useTransform(scrollYProgress, [0, 0.3], [8, 0]);

  // Background effects
  const backgroundY = useTransform(scrollYProgress, [0, 1], [0, -100]);
  const overlayOpacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 0.1, 0.3, 0.5]);

  // Text animations
  const titleY = useTransform(scrollYProgress, [0, 0.3], [0, -80]);
  const titleOpacity = useTransform(scrollYProgress, [0, 0.2, 0.4], [1, 0.7, 0]);

  return (
    <div ref={containerRef} className="relative">
      {/* Much shorter spacer - only 120vh instead of 200vh */}
      <div className="h-[120vh]" />

      {/* Sticky container */}
      <div className="sticky top-0 h-screen overflow-hidden">
        {/* Subtle background gradient that moves with scroll */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-success-50"
          style={{ y: backgroundY }}
        />

        {/* Very subtle overlay */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-b from-transparent via-primary-900/10 to-primary-900/20"
          style={{ opacity: overlayOpacity }}
        />

        {/* Demo title that fades as demo comes into focus */}
        <motion.div
          className="absolute inset-x-0 top-20 z-20 text-center px-4"
          style={{
            y: titleY,
            opacity: titleOpacity
          }}
        >
          <motion.div
            className="inline-flex items-center gap-2 bg-gradient-to-r from-primary-600 to-success-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-4"
            animate={{
              boxShadow: [
                "0 4px 14px 0 rgba(59, 130, 246, 0.2)",
                "0 6px 20px 0 rgba(16, 185, 129, 0.3)",
                "0 4px 14px 0 rgba(59, 130, 246, 0.2)"
              ]
            }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <span>⚡</span>
            <span>Live Demo</span>
          </motion.div>

          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
            See Respire in Action
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Interactive dashboard with real-time AI predictions
          </p>
        </motion.div>

        {/* The demo - positioned to feel natural */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center px-4 z-10"
          style={{
            y: demoY,
            scale: demoScale,
            opacity: demoOpacity,
            rotateX: demoRotateX,
            perspective: "1000px"
          }}
        >
          <div className="w-full max-w-7xl">
            {/* Subtle glow effect */}
            <motion.div
              className="absolute inset-0 rounded-3xl blur-xl"
              animate={{
                background: [
                  "radial-gradient(ellipse at center, rgba(59, 130, 246, 0.1) 0%, transparent 70%)",
                  "radial-gradient(ellipse at center, rgba(16, 185, 129, 0.15) 0%, transparent 70%)",
                  "radial-gradient(ellipse at center, rgba(139, 92, 246, 0.1) 0%, transparent 70%)"
                ]
              }}
              transition={{ duration: 6, repeat: Infinity }}
            />

            {/* Demo container with subtle border */}
            <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-6 sm:p-8 relative">
              {/* Very subtle animated border */}
              <motion.div
                className="absolute inset-0 rounded-3xl"
                animate={{
                  background: [
                    "linear-gradient(0deg, transparent, rgba(59, 130, 246, 0.1), transparent)",
                    "linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.1), transparent)",
                    "linear-gradient(180deg, transparent, rgba(139, 92, 246, 0.1), transparent)",
                    "linear-gradient(270deg, transparent, rgba(59, 130, 246, 0.1), transparent)"
                  ]
                }}
                transition={{ duration: 8, repeat: Infinity }}
                style={{ padding: "1px" }}
              >
                <div className="w-full h-full bg-transparent rounded-3xl" />
              </motion.div>

              {/* Demo content */}
              <div className="relative z-10">
                <EnhancedDashboardDemo />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Bottom CTA that appears smoothly */}
        <motion.div
          className="absolute bottom-8 inset-x-0 z-20 text-center px-4"
          style={{
            opacity: useTransform(scrollYProgress, [0.7, 0.9], [0, 1]),
            y: useTransform(scrollYProgress, [0.7, 0.9], [20, 0])
          }}
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-gradient-to-r from-primary-600 to-success-600 hover:from-primary-700 hover:to-success-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg transition-all duration-200"
            onClick={() => {
              document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            Explore All Features →
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
};