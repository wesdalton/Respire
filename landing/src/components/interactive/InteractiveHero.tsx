import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion';
import { Play, ArrowRight, Activity, Sparkles, MousePointer2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { trustedCompanies, stats } from '../../data/mockData';
import { FloatingDashboardPreview } from './FloatingDashboardPreview';

export const InteractiveHero: React.FC = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const [currentStatIndex, setCurrentStatIndex] = useState(0);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 150, damping: 15 });
  const springY = useSpring(mouseY, { stiffness: 150, damping: 15 });

  // Mouse tracking for interactive elements
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const y = ((e.clientY - rect.top) / rect.height) * 2 - 1;

    setMousePosition({ x, y });
    mouseX.set(x * 20);
    mouseY.set(y * 20);
  }, [mouseX, mouseY]);

  // Cycle through stats
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStatIndex((prev) => (prev + 1) % stats.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: 'easeOut' }
    }
  };

  return (
    <section
      className="relative min-h-screen flex items-center justify-center overflow-hidden cursor-none"
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* Custom Cursor */}
      <motion.div
        className="fixed top-0 left-0 w-6 h-6 bg-primary-500 rounded-full pointer-events-none z-50 mix-blend-difference"
        style={{
          x: springX,
          y: springY,
        }}
        animate={{
          scale: isHovering ? 1.5 : 1,
          opacity: isHovering ? 0.8 : 0.6
        }}
      />

      {/* Interactive Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-success-50">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />

        {/* Animated Mesh Gradient */}
        <motion.div
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(600px circle at ${50 + mousePosition.x * 10}% ${50 + mousePosition.y * 10}%,
              rgba(59, 130, 246, 0.1) 0%,
              rgba(16, 185, 129, 0.1) 50%,
              transparent 100%)`
          }}
        />
      </div>

      {/* Floating Interactive Elements */}
      <motion.div
        animate={{
          y: [0, -20, 0],
          rotate: [0, 5, 0],
          scale: [1, 1.1, 1]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
        style={{
          x: mousePosition.x * 30,
          y: mousePosition.y * 20
        }}
        className="absolute top-20 left-10 w-32 h-32 bg-gradient-to-br from-primary-400 to-primary-600 rounded-3xl blur-xl opacity-20"
      />

      <motion.div
        animate={{
          y: [0, 15, 0],
          rotate: [0, -3, 0],
          scale: [1, 1.05, 1]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 1
        }}
        style={{
          x: mousePosition.x * -25,
          y: mousePosition.y * 15
        }}
        className="absolute top-40 right-20 w-24 h-24 bg-gradient-to-br from-success-400 to-success-600 rounded-full blur-2xl opacity-25"
      />

      {/* Floating Dashboard Preview */}
      <FloatingDashboardPreview />

      <div className="container-max relative z-10">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="text-center px-4 sm:px-6 lg:px-8"
        >
          {/* Interactive Announcement Badge */}
          <motion.div variants={itemVariants} className="mb-8">
            <motion.div
              whileHover={{ scale: 1.05, rotate: 1 }}
              whileTap={{ scale: 0.95 }}
              className="inline-block"
            >
              <Badge variant="primary" size="lg" className="inline-flex items-center gap-2 cursor-pointer">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                >
                  <Activity className="w-4 h-4" />
                </motion.div>
                <span className="relative">
                  Now trusted by 500+ teams worldwide
                  <motion.div
                    className="absolute -inset-1 bg-primary-400 rounded blur opacity-25"
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.25, 0.4, 0.25]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </span>
              </Badge>
            </motion.div>
          </motion.div>

          {/* Interactive Main Headline */}
          <motion.h1
            variants={itemVariants}
            className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight mb-6 relative"
          >
            <motion.span
              className="text-gray-900 inline-block"
              whileHover={{
                scale: 1.02,
                textShadow: "0px 0px 8px rgba(59,130,246,0.3)"
              }}
            >
              Prevent Burnout
            </motion.span>
            <br />
            <motion.span
              className="text-gradient inline-block relative"
              whileHover={{
                scale: 1.05,
                filter: "brightness(1.2)"
              }}
            >
              Before It Happens
              <motion.div
                className="absolute -bottom-2 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 to-success-500 rounded"
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 1.5, delay: 1 }}
              />
            </motion.span>
          </motion.h1>

          {/* Interactive Subheadline */}
          <motion.p
            variants={itemVariants}
            className="text-xl sm:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed"
          >
            AI-powered insights from your wearable data help you optimize performance
            and protect mental health with{' '}
            <motion.span
              className="text-primary-600 font-semibold relative cursor-pointer"
              whileHover={{
                scale: 1.1,
                color: "#1D4ED8"
              }}
            >
              94% accuracy
              <motion.div
                className="absolute -top-6 left-1/2 transform -translate-x-1/2"
                initial={{ opacity: 0, y: 10 }}
                whileHover={{ opacity: 1, y: 0 }}
              >
                <div className="bg-gray-900 text-white px-2 py-1 rounded text-xs whitespace-nowrap">
                  Based on 10,000+ predictions
                </div>
              </motion.div>
            </motion.span>
          </motion.p>

          {/* Interactive CTA Buttons */}
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
          >
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                variant="primary"
                size="xl"
                icon={ArrowRight}
                iconPosition="right"
                className="w-full sm:w-auto group relative overflow-hidden"
                onClick={() => {
                  window.scrollTo({ top: window.innerHeight * 0.8, behavior: 'smooth' });
                }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-primary-700 to-primary-800"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: "0%" }}
                  transition={{ duration: 0.3 }}
                />
                <span className="relative z-10">Try Interactive Demo</span>
              </Button>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                variant="outline"
                size="xl"
                icon={Play}
                className="w-full sm:w-auto group"
              >
                <motion.div
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="mr-2"
                >
                  <Play className="w-5 h-5" />
                </motion.div>
                Watch Demo
              </Button>
            </motion.div>
          </motion.div>

          {/* Interactive Rotating Stats */}
          <motion.div
            variants={itemVariants}
            className="grid grid-cols-2 lg:grid-cols-4 gap-8 mb-12"
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStatIndex}
                initial={{ opacity: 0, y: 20, rotateY: -90 }}
                animate={{ opacity: 1, y: 0, rotateY: 0 }}
                exit={{ opacity: 0, y: -20, rotateY: 90 }}
                transition={{ duration: 0.6 }}
                className="lg:col-span-4 text-center"
              >
                <div className="text-6xl sm:text-7xl font-bold text-gradient mb-2 relative">
                  {stats[currentStatIndex].value}
                  <motion.div
                    className="absolute -inset-4 bg-gradient-to-r from-primary-200 to-success-200 rounded-lg opacity-20"
                    animate={{
                      scale: [1, 1.1, 1],
                      rotate: [0, 1, 0]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
                <div className="text-lg text-gray-600 mb-4">{stats[currentStatIndex].label}</div>

                {/* Progress indicator */}
                <div className="flex justify-center space-x-2">
                  {stats.map((_, index) => (
                    <motion.div
                      key={index}
                      className={`w-2 h-2 rounded-full cursor-pointer ${
                        index === currentStatIndex ? 'bg-primary-500' : 'bg-gray-300'
                      }`}
                      onClick={() => setCurrentStatIndex(index)}
                      whileHover={{ scale: 1.2 }}
                      whileTap={{ scale: 0.9 }}
                    />
                  ))}
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>

          {/* Interactive Trust Bar */}
          <motion.div variants={itemVariants} className="space-y-4">
            <motion.p
              className="text-sm text-gray-500 font-medium flex items-center justify-center gap-2"
              animate={{
                color: ["#6B7280", "#3B82F6", "#6B7280"]
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              <Sparkles className="w-4 h-4" />
              Trusted by high-performing teams at
            </motion.p>
            <div className="flex flex-wrap items-center justify-center gap-8 opacity-60 hover:opacity-100 transition-all duration-500">
              {trustedCompanies.slice(0, 6).map((company, index) => (
                <motion.div
                  key={company.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{
                    scale: 1.2,
                    opacity: 1,
                    y: -5,
                    filter: "grayscale(0%)"
                  }}
                  className="h-8 flex items-center cursor-pointer grayscale hover:grayscale-0 transition-all duration-300"
                >
                  <div className="text-2xl font-bold text-gray-400 hover:text-gray-700 transition-colors">
                    {company.name}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Interactive Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2, duration: 0.5 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2 cursor-pointer"
        onClick={() => {
          window.scrollTo({ top: window.innerHeight * 0.8, behavior: 'smooth' });
        }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center relative group"
        >
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-1 h-3 bg-gray-400 rounded-full mt-2 group-hover:bg-primary-500 transition-colors"
          />
          <div className="absolute -bottom-8 text-xs text-gray-500 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
            Explore Demo
          </div>
        </motion.div>
      </motion.div>

      {/* Pointer hint for first-time visitors */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 3, duration: 1 }}
        className="absolute top-1/2 right-8 transform -translate-y-1/2"
      >
        <motion.div
          animate={{
            x: [0, 10, 0],
            y: [0, -5, 0]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="flex items-center space-x-2 text-gray-400 text-sm"
        >
          <MousePointer2 className="w-4 h-4" />
          <span>Move your mouse</span>
        </motion.div>
      </motion.div>
    </section>
  );
};