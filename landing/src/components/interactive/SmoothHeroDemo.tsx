import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useSpring, useScroll, useTransform } from 'framer-motion';
import { Play, ArrowRight, Activity, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { trustedCompanies, stats } from '../../data/mockData';
import { EnhancedDashboardDemo } from './EnhancedDashboardDemo';

export const SmoothHeroDemo: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const [currentStatIndex, setCurrentStatIndex] = useState(0);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 100, damping: 20, mass: 0.5 });
  const springY = useSpring(mouseY, { stiffness: 100, damping: 20, mass: 0.5 });

  // Smooth scroll-based animations with proper ranges
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  // Hero content - stable, no disappearing
  const heroOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0.3]);
  const heroY = useTransform(scrollYProgress, [0, 0.8], [0, -20]);

  // Demo animations - integrated page flow
  const demoY = useTransform(scrollYProgress, [0, 0.4, 0.8, 1], [0, 0, 0, 50]);
  const demoScale = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0.8, 1, 1, 0.95]);
  const demoOpacity = useTransform(scrollYProgress, [0, 0.2, 0.7, 0.9, 1], [0, 1, 1, 0.8, 0]);

  // Background - smooth transition to demo background
  const backgroundOpacity = useTransform(scrollYProgress, [0.3, 0.6], [0, 1]);
  const demoBackgroundOpacity = useTransform(scrollYProgress, [0.4, 0.7], [0, 1]);

  // Mouse tracking with throttling for performance
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const y = ((e.clientY - rect.top) / rect.height) * 2 - 1;

    setMousePosition({ x, y });
    mouseX.set(x * 15); // Reduced intensity for smoother performance
    mouseY.set(y * 15);
  }, [mouseX, mouseY]);

  // Cycle through stats
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStatIndex((prev) => (prev + 1) % stats.length);
    }, 4000); // Slower for better UX
    return () => clearInterval(interval);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: [0.25, 0.46, 0.45, 0.94] } // Custom bezier for smoothness
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative min-h-[120vh] overflow-hidden" // Allow scroll to continue
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* Smooth Custom Cursor */}
      <motion.div
        className="fixed top-0 left-0 w-4 h-4 bg-primary-500 rounded-full pointer-events-none z-50 mix-blend-difference"
        style={{
          x: springX,
          y: springY,
        }}
        animate={{
          scale: isHovering ? 1.2 : 1,
          opacity: isHovering ? 0.8 : 0.5
        }}
        transition={{ duration: 0.2 }}
      />

      {/* Base Background - always present */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary-50 via-white to-success-50 z-0" />

      {/* Demo Background - fades in smoothly */}
      <motion.div
        className="fixed inset-0 bg-gradient-to-br from-gray-100 via-white to-primary-100 z-1"
        style={{ opacity: demoBackgroundOpacity }}
      />

      {/* Subtle animated elements */}
      <motion.div
        className="fixed top-20 left-10 w-24 h-24 bg-gradient-to-br from-primary-400/20 to-primary-600/20 rounded-3xl blur-xl z-10"
        animate={{
          y: [0, -15, 0],
          scale: [1, 1.05, 1]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        style={{
          x: mousePosition.x * 20,
          y: mousePosition.y * 15
        }}
      />

      {/* Hero Content */}
      <motion.div
        className="sticky top-0 h-screen flex items-center justify-center z-20"
        style={{
          opacity: heroOpacity,
          y: heroY
        }}
      >
        <div className="container-max">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="text-center px-4 sm:px-6 lg:px-8"
          >
            {/* Badge */}
            <motion.div variants={itemVariants} className="mb-8">
              <Badge variant="primary" size="lg" className="inline-flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                >
                  <Activity className="w-4 h-4" />
                </motion.div>
                <span>Now trusted by 500+ teams worldwide</span>
              </Badge>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              variants={itemVariants}
              className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight mb-6"
            >
              <span className="text-gray-900 block">Prevent Burnout</span>
              <span className="text-gradient block">Before It Happens</span>
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              variants={itemVariants}
              className="text-xl sm:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed"
            >
              AI-powered insights from your wearable data help you optimize performance
              and protect mental health with{' '}
              <span className="text-primary-600 font-semibold">94% accuracy</span>
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              variants={itemVariants}
              className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
            >
              <Button
                variant="primary"
                size="xl"
                icon={ArrowRight}
                iconPosition="right"
                className="w-full sm:w-auto"
                onClick={() => {
                  window.scrollTo({ top: window.innerHeight * 0.4, behavior: 'smooth' });
                }}
              >
                Try Interactive Demo
              </Button>

              <Button
                variant="outline"
                size="xl"
                icon={Play}
                className="w-full sm:w-auto"
              >
                Watch Demo
              </Button>
            </motion.div>

            {/* Rotating Stats */}
            <motion.div
              variants={itemVariants}
              className="mb-12"
            >
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentStatIndex}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.6, ease: "easeInOut" }}
                  className="text-center"
                >
                  <div className="text-5xl sm:text-6xl font-bold text-gradient mb-2">
                    {stats[currentStatIndex].value}
                  </div>
                  <div className="text-lg text-gray-600">{stats[currentStatIndex].label}</div>
                </motion.div>
              </AnimatePresence>
            </motion.div>

            {/* Trust Bar */}
            <motion.div variants={itemVariants} className="space-y-4">
              <p className="text-sm text-gray-500 font-medium flex items-center justify-center gap-2">
                <Sparkles className="w-4 h-4" />
                Trusted by high-performing teams at
              </p>
              <div className="flex flex-wrap items-center justify-center gap-8 opacity-60">
                {trustedCompanies.slice(0, 6).map((company, index) => (
                  <motion.div
                    key={company.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="h-8 flex items-center grayscale hover:grayscale-0 transition-all duration-300"
                  >
                    <div className="text-xl font-bold text-gray-400">
                      {company.name}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>

      {/* Demo Section - Integrated into page flow */}
      <div className="relative z-30">
        <motion.div
          className="container mx-auto px-4"
          style={{
            y: demoY,
            scale: demoScale,
            opacity: demoOpacity
          }}
        >
          {/* Demo emerges naturally from page content */}
          <motion.div
            className="bg-white rounded-3xl shadow-2xl border border-gray-200 p-8 mx-auto max-w-7xl"
            style={{
              transform: useTransform(scrollYProgress, [0, 0.3, 0.7], ["translateY(20vh)", "translateY(0vh)", "translateY(0vh)"])
            }}
          >

            {/* Demo content container */}
            <div className="relative max-h-[70vh] overflow-hidden">
              <EnhancedDashboardDemo />
            </div>
          </motion.div>

        </motion.div>
      </div>

    </div>
  );
};