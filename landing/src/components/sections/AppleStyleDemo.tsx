import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ScrollDemoReveal } from '../interactive/ScrollDemoReveal';

export const AppleStyleDemo: React.FC = () => {
  const sectionRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });

  // Create a seamless transition from hero to demo
  const backgroundOpacity = useTransform(scrollYProgress, [0, 0.1, 0.9, 1], [0, 1, 1, 0]);
  const textY = useTransform(scrollYProgress, [0, 0.2], [0, -100]);
  const textOpacity = useTransform(scrollYProgress, [0, 0.15, 0.3], [1, 0.5, 0]);

  return (
    <section
      ref={sectionRef}
      className="relative min-h-[300vh]" // Extra height for scroll effect
    >
      {/* Transition background */}
      <motion.div
        className="fixed inset-0 bg-gradient-to-b from-gray-50 via-gray-100 to-gray-900 z-0"
        style={{ opacity: backgroundOpacity }}
      />

      {/* Introduction text that fades out */}
      <motion.div
        className="sticky top-0 h-screen flex items-center justify-center z-10"
        style={{ y: textY, opacity: textOpacity }}
      >
        <div className="text-center px-4 max-w-4xl">
          <motion.h2
            className="text-5xl sm:text-7xl font-bold mb-8"
            animate={{
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
            }}
            transition={{ duration: 6, repeat: Infinity }}
            style={{
              background: "linear-gradient(90deg, #111827, #3B82F6, #10B981, #111827)",
              backgroundSize: "200% 100%",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              color: "transparent"
            }}
          >
            The Future of
            <br />
            Workplace Wellness
          </motion.h2>

          <motion.p
            className="text-xl text-gray-600 mb-8 leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            Powered by artificial intelligence and real-time health data,
            <br />
            Respire prevents burnout before it happens.
          </motion.p>

          <motion.div
            className="flex items-center justify-center space-x-2 text-gray-500"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <span className="text-sm">Scroll to explore</span>
            <motion.svg
              className="w-4 h-4"
              animate={{ y: [0, 4, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </motion.svg>
          </motion.div>
        </div>
      </motion.div>

      {/* The Apple-style demo reveal */}
      <ScrollDemoReveal />

      {/* Spacer to ensure smooth scrolling to next section */}
      <div className="h-screen" />
    </section>
  );
};