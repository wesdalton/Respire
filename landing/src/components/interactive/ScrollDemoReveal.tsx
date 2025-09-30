import React, { useRef } from 'react';
import { motion, useScroll, useTransform, MotionValue } from 'framer-motion';
import { EnhancedDashboardDemo } from './EnhancedDashboardDemo';

interface ScrollDemoRevealProps {
  children?: React.ReactNode;
}

export const ScrollDemoReveal: React.FC<ScrollDemoRevealProps> = ({ children }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });

  // Transform values for the demo reveal effect
  const demoY = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [200, 0, 0, -100]);
  const demoScale = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0.8, 1, 1, 1.05]);
  const demoOpacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  const demoRotateX = useTransform(scrollYProgress, [0, 0.3, 0.7], [15, 0, 0]);

  // Background and overlay effects
  const backgroundScale = useTransform(scrollYProgress, [0, 0.5, 1], [1, 1.1, 1.2]);
  const overlayOpacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 0.3, 0.8, 1]);

  // Text and content transforms
  const headerY = useTransform(scrollYProgress, [0, 0.3, 0.7], [0, -50, -150]);
  const headerOpacity = useTransform(scrollYProgress, [0, 0.2, 0.4], [1, 0.5, 0]);
  const contentY = useTransform(scrollYProgress, [0.6, 0.8, 1], [0, -50, -100]);
  const contentOpacity = useTransform(scrollYProgress, [0.6, 0.8, 1], [1, 0.5, 0]);

  return (
    <div ref={containerRef} className="relative">
      {/* Spacer for scroll distance */}
      <div className="h-[200vh]" />

      {/* Sticky container */}
      <div className="sticky top-0 h-screen overflow-hidden">
        {/* Animated background */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-gray-900 via-primary-900 to-black"
          style={{
            scale: backgroundScale,
            opacity: overlayOpacity
          }}
        />

        {/* Dynamic gradient overlay */}
        <motion.div
          className="absolute inset-0"
          style={{
            background: useTransform(
              scrollYProgress,
              [0, 0.5, 1],
              [
                "radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1), transparent 70%)",
                "radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.2), transparent 70%)",
                "radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.3), transparent 70%)"
              ]
            )
          }}
        />

        {/* Section Header - fades out as demo rises */}
        <motion.div
          className="absolute inset-x-0 top-16 z-30 text-center px-4"
          style={{
            y: headerY,
            opacity: headerOpacity
          }}
        >
          <motion.div
            className="inline-flex items-center gap-3 bg-white text-gray-900 px-6 py-3 rounded-full mb-6 shadow-xl"
            animate={{
              boxShadow: [
                "0 10px 25px rgba(0, 0, 0, 0.1)",
                "0 20px 40px rgba(59, 130, 246, 0.3)",
                "0 10px 25px rgba(0, 0, 0, 0.1)"
              ]
            }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            >
              ⚡
            </motion.div>
            <span className="font-semibold">Scroll to Experience</span>
          </motion.div>

          <motion.h2
            className="text-4xl sm:text-6xl font-bold mb-6 text-white"
            animate={{
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
            }}
            transition={{ duration: 8, repeat: Infinity }}
            style={{
              background: "linear-gradient(90deg, #FFFFFF, #3B82F6, #10B981, #FFFFFF)",
              backgroundSize: "300% 100%",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              color: "transparent"
            }}
          >
            Watch Respire Rise
          </motion.h2>

          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            See how our AI-powered platform emerges to transform your workflow
          </p>
        </motion.div>

        {/* Demo Container - the star of the show */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center px-4 z-20"
          style={{
            y: demoY,
            scale: demoScale,
            opacity: demoOpacity,
            rotateX: demoRotateX,
            perspective: "1000px"
          }}
        >
          <motion.div
            className="w-full max-w-7xl relative"
            animate={{
              rotateY: [0, 1, -1, 0]
            }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            style={{ transformStyle: "preserve-3d" }}
          >
            {/* Glowing border effect */}
            <motion.div
              className="absolute inset-0 rounded-3xl z-0"
              animate={{
                background: [
                  "linear-gradient(0deg, #3B82F6, #10B981, #8B5CF6, #F59E0B)",
                  "linear-gradient(90deg, #3B82F6, #10B981, #8B5CF6, #F59E0B)",
                  "linear-gradient(180deg, #3B82F6, #10B981, #8B5CF6, #F59E0B)",
                  "linear-gradient(270deg, #3B82F6, #10B981, #8B5CF6, #F59E0B)"
                ]
              }}
              transition={{ duration: 4, repeat: Infinity }}
              style={{
                padding: "3px",
                backgroundSize: "400% 400%",
                filter: "blur(1px)"
              }}
            >
              <div className="w-full h-full bg-white rounded-3xl" />
            </motion.div>

            {/* Outer glow */}
            <motion.div
              className="absolute inset-0 rounded-3xl"
              animate={{
                boxShadow: [
                  "0 0 50px rgba(59, 130, 246, 0.3)",
                  "0 0 80px rgba(16, 185, 129, 0.4)",
                  "0 0 50px rgba(139, 92, 246, 0.3)",
                  "0 0 50px rgba(59, 130, 246, 0.3)"
                ]
              }}
              transition={{ duration: 4, repeat: Infinity }}
            />

            {/* Demo content */}
            <div className="bg-white rounded-3xl shadow-2xl p-8 relative z-10 backdrop-blur-sm">
              {/* Floating particles around the demo */}
              {[...Array(6)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 bg-gradient-to-r from-primary-400 to-success-400 rounded-full"
                  style={{
                    left: `${10 + (i % 3) * 30}%`,
                    top: `${10 + Math.floor(i / 3) * 80}%`
                  }}
                  animate={{
                    y: [0, -20, 0],
                    opacity: [0.3, 1, 0.3],
                    scale: [0.8, 1.2, 0.8]
                  }}
                  transition={{
                    duration: 3 + i * 0.5,
                    repeat: Infinity,
                    delay: i * 0.3,
                    ease: "easeInOut"
                  }}
                />
              ))}

              <EnhancedDashboardDemo />
            </div>
          </motion.div>
        </motion.div>

        {/* Bottom content that appears after demo is revealed */}
        <motion.div
          className="absolute bottom-16 inset-x-0 z-30 text-center px-4"
          style={{
            y: contentY,
            opacity: contentOpacity
          }}
        >
          <motion.button
            whileHover={{
              scale: 1.05,
              boxShadow: "0 20px 40px rgba(255, 255, 255, 0.2)"
            }}
            whileTap={{ scale: 0.95 }}
            className="bg-white hover:bg-gray-50 text-gray-900 font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-200 shadow-xl"
            onClick={() => {
              document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            Experience the Full Platform →
          </motion.button>
          <p className="text-gray-300 text-sm mt-4">
            Ready to transform your team's wellbeing?
          </p>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-30"
          style={{
            opacity: useTransform(scrollYProgress, [0, 0.2], [1, 0])
          }}
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center"
          >
            <motion.div
              animate={{ y: [0, 12, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-1 h-3 bg-white/70 rounded-full mt-2"
            />
          </motion.div>
          <p className="text-white/70 text-xs mt-2">Scroll to reveal</p>
        </motion.div>
      </div>
    </div>
  );
};