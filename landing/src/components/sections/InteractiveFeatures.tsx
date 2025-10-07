import React, { useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Activity, Brain, Users, Zap, Shield, Smartphone, TrendingUp, Globe, ChevronRight, Sparkles } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

const features = [
  {
    id: 'monitoring',
    title: 'Real-Time Health Monitoring',
    description: 'Connect any wearable device and get comprehensive health insights updated every 15 minutes.',
    icon: Activity,
    color: 'text-primary-500',
    bgGradient: 'from-primary-50 to-primary-100',
    stats: ['15+ supported devices', '24/7 monitoring', 'Sub-second latency'],
    demoElement: {
      type: 'pulse',
      color: '#3B82F6'
    }
  },
  {
    id: 'ai',
    title: 'Predictive AI Models',
    description: 'Ensemble machine learning models predict burnout risk 3-7 days in advance with 94% accuracy.',
    icon: Brain,
    color: 'text-success-500',
    bgGradient: 'from-success-50 to-success-100',
    stats: ['94% accuracy', 'Ensemble ML models', 'Explainable AI'],
    demoElement: {
      type: 'neural',
      color: '#10B981'
    }
  },
  {
    id: 'team',
    title: 'Team & Enterprise Analytics',
    description: 'Organization-wide insights help managers prevent team burnout before it impacts performance.',
    icon: Users,
    color: 'text-warning-500',
    bgGradient: 'from-warning-50 to-warning-100',
    stats: ['Team heatmaps', 'Manager insights', 'Anonymous analytics'],
    demoElement: {
      type: 'network',
      color: '#F59E0B'
    }
  },
  {
    id: 'integrations',
    title: 'Seamless Integrations',
    description: 'Works with your existing workflow through 50+ integrations and a comprehensive API.',
    icon: Zap,
    color: 'text-purple-500',
    bgGradient: 'from-purple-50 to-purple-100',
    stats: ['50+ integrations', 'REST API', 'Webhooks'],
    demoElement: {
      type: 'connection',
      color: '#8B5CF6'
    }
  }
];

const FeatureDemoElement: React.FC<{ feature: typeof features[0], isActive: boolean }> = ({ feature, isActive }) => {
  const variants = {
    pulse: (
      <div className="relative w-full h-full flex items-center justify-center">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-12 h-12 rounded-full border-2"
            style={{ borderColor: feature.demoElement.color }}
            animate={isActive ? {
              scale: [1, 2, 3],
              opacity: [1, 0.5, 0],
            } : {}}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.4,
              ease: "easeOut"
            }}
          />
        ))}
        <div
          className="w-4 h-4 rounded-full"
          style={{ backgroundColor: feature.demoElement.color }}
        />
      </div>
    ),
    neural: (
      <div className="w-full h-full flex items-center justify-center">
        <svg width="80" height="80" viewBox="0 0 80 80">
          {/* Neural network nodes */}
          <motion.circle cx="20" cy="20" r="4" fill={feature.demoElement.color}
            animate={isActive ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity, delay: 0 }}
          />
          <motion.circle cx="60" cy="20" r="4" fill={feature.demoElement.color}
            animate={isActive ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
          />
          <motion.circle cx="20" cy="60" r="4" fill={feature.demoElement.color}
            animate={isActive ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
          />
          <motion.circle cx="60" cy="60" r="4" fill={feature.demoElement.color}
            animate={isActive ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity, delay: 0.6 }}
          />
          <motion.circle cx="40" cy="40" r="6" fill={feature.demoElement.color}
            animate={isActive ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity, delay: 0.8 }}
          />

          {/* Connections */}
          <motion.line x1="20" y1="20" x2="40" y2="40" stroke={feature.demoElement.color} strokeWidth="2"
            animate={isActive ? { opacity: [0.3, 1, 0.3] } : {}}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <motion.line x1="60" y1="20" x2="40" y2="40" stroke={feature.demoElement.color} strokeWidth="2"
            animate={isActive ? { opacity: [0.3, 1, 0.3] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
          />
          <motion.line x1="20" y1="60" x2="40" y2="40" stroke={feature.demoElement.color} strokeWidth="2"
            animate={isActive ? { opacity: [0.3, 1, 0.3] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 1 }}
          />
          <motion.line x1="60" y1="60" x2="40" y2="40" stroke={feature.demoElement.color} strokeWidth="2"
            animate={isActive ? { opacity: [0.3, 1, 0.3] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 1.5 }}
          />
        </svg>
      </div>
    ),
    network: (
      <div className="w-full h-full relative">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-3 h-3 rounded-full"
            style={{
              backgroundColor: feature.demoElement.color,
              left: `${20 + (i % 3) * 30}%`,
              top: `${30 + Math.floor(i / 3) * 40}%`
            }}
            animate={isActive ? {
              scale: [1, 1.5, 1],
              opacity: [0.7, 1, 0.7]
            } : {}}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: i * 0.2
            }}
          />
        ))}
      </div>
    ),
    connection: (
      <div className="w-full h-full flex items-center justify-center">
        <motion.div
          className="flex items-center space-x-2"
          animate={isActive ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-4 h-4 rounded border-2" style={{ borderColor: feature.demoElement.color }} />
          <motion.div
            className="w-8 h-0.5"
            style={{ backgroundColor: feature.demoElement.color }}
            animate={isActive ? { scaleX: [0, 1, 0] } : {}}
            transition={{ duration: 1, repeat: Infinity, repeatDelay: 1 }}
          />
          <div className="w-4 h-4 rounded border-2" style={{ borderColor: feature.demoElement.color }} />
        </motion.div>
      </div>
    )
  };

  return variants[feature.demoElement.type as keyof typeof variants];
};

export const InteractiveFeatures: React.FC = () => {
  const [selectedFeature, setSelectedFeature] = useState(features[0]);
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: false, amount: 0.3 });


  return (
    <section ref={ref} id="features" className="section-padding bg-gradient-to-br from-white via-gray-50 to-primary-50">
      <div className="container-max">
        {/* Enhanced Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-center mb-16"
        >
          <Badge variant="primary" size="lg" className="mb-4 inline-flex items-center gap-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-4 h-4" />
            </motion.div>
            Platform Features
          </Badge>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Everything you need
            <br />
            to prevent burnout
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From real-time monitoring to predictive analytics, our comprehensive platform
            provides the tools and insights you need to maintain optimal performance.
          </p>
        </motion.div>

        {/* Interactive Features Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* Feature Selection Cards */}
          <div className="space-y-4">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              const isSelected = selectedFeature.id === feature.id;
              const isHovered = hoveredFeature === feature.id;

              return (
                <motion.div
                  key={feature.id}
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, amount: 0.3 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{
                    scale: 1.02,
                    y: -4,
                    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
                  }}
                  onClick={() => setSelectedFeature(feature)}
                  onMouseEnter={() => setHoveredFeature(feature.id)}
                  onMouseLeave={() => setHoveredFeature(null)}
                  className={`cursor-pointer transition-all duration-300 ${
                    isSelected
                      ? 'ring-2 ring-primary-500 ring-offset-4 shadow-xl'
                      : 'hover:shadow-lg'
                  }`}
                >
                  <Card className={`p-6 relative overflow-hidden ${
                    isSelected
                      ? `bg-gradient-to-br ${feature.bgGradient} border-primary-200`
                      : 'hover:bg-gray-50'
                  }`}>
                    {/* Animated background pattern */}
                    {isSelected && (
                      <motion.div
                        className="absolute inset-0 opacity-10"
                        animate={{
                          backgroundPosition: ["0% 0%", "100% 100%"]
                        }}
                        transition={{ duration: 20, repeat: Infinity }}
                        style={{
                          background: `linear-gradient(45deg, ${feature.demoElement.color}22 0%, transparent 50%, ${feature.demoElement.color}22 100%)`,
                          backgroundSize: "20px 20px"
                        }}
                      />
                    )}

                    <div className="flex items-start space-x-4 relative z-10">
                      <motion.div
                        className={`p-3 rounded-xl ${
                          isSelected ? 'bg-white shadow-md' : 'bg-gray-100'
                        }`}
                        animate={isSelected ? {
                          scale: [1, 1.1, 1],
                          rotate: [0, 5, -5, 0]
                        } : {}}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <Icon className={`w-6 h-6 ${
                          isSelected ? 'text-primary-600' : feature.color
                        }`} />
                      </motion.div>

                      <div className="flex-1 min-w-0">
                        <motion.h3
                          className="text-lg font-semibold text-gray-900 mb-2"
                          animate={isHovered ? { x: 4 } : {}}
                          transition={{ duration: 0.2 }}
                        >
                          {feature.title}
                          {isSelected && (
                            <motion.span
                              className="ml-2 text-primary-600"
                              animate={{ opacity: [0, 1, 0] }}
                              transition={{ duration: 1, repeat: Infinity }}
                            >
                              <ChevronRight className="w-4 h-4 inline" />
                            </motion.span>
                          )}
                        </motion.h3>
                        <p className="text-gray-600 mb-4">
                          {feature.description}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {feature.stats.map((stat, i) => (
                            <motion.div
                              key={stat}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={isSelected ? { opacity: 1, scale: 1 } : { opacity: 1, scale: 1 }}
                              transition={{ delay: i * 0.1 }}
                            >
                              <Badge
                                variant={isSelected ? 'primary' : 'neutral'}
                                size="sm"
                                className={isSelected ? 'animate-pulse' : ''}
                              >
                                {stat}
                              </Badge>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>

          {/* Interactive Feature Details */}
          <motion.div
            key={selectedFeature.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="lg:sticky lg:top-24"
          >
            <div>
              <Card className="p-8 relative overflow-hidden">
                {/* Interactive background */}
                <motion.div
                  className="absolute inset-0 opacity-5"
                  animate={{
                    scale: [1, 1.05, 1],
                    rotate: [0, 1, 0]
                  }}
                  transition={{ duration: 6, repeat: Infinity }}
                  style={{
                    background: `radial-gradient(circle at 50% 50%, ${selectedFeature.demoElement.color}, transparent 70%)`
                  }}
                />

                <div className="flex items-center space-x-4 mb-6 relative z-10">
                  <motion.div
                    className="p-4 bg-primary-100 rounded-xl"
                    animate={{
                      boxShadow: [
                        "0 0 0 0 rgba(59, 130, 246, 0)",
                        "0 0 0 20px rgba(59, 130, 246, 0.1)",
                        "0 0 0 0 rgba(59, 130, 246, 0)"
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <selectedFeature.icon className="w-8 h-8 text-primary-600" />
                  </motion.div>
                  <div>
                    <motion.h3
                      className="text-2xl font-bold text-gray-900"
                      animate={{ color: ["#111827", selectedFeature.demoElement.color, "#111827"] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    >
                      {selectedFeature.title}
                    </motion.h3>
                    <div className="flex items-center space-x-2 mt-2">
                      <TrendingUp className="w-4 h-4 text-success-500" />
                      <span className="text-sm text-success-600 font-medium">
                        Production Ready
                      </span>
                    </div>
                  </div>
                </div>

                {/* Interactive Demo Element */}
                <motion.div
                  className="w-full h-32 mb-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg flex items-center justify-center"
                  animate={{ backgroundColor: ["#F9FAFB", `${selectedFeature.demoElement.color}08`, "#F9FAFB"] }}
                  transition={{ duration: 4, repeat: Infinity }}
                >
                  <FeatureDemoElement feature={selectedFeature} isActive={true} />
                </motion.div>

                <p className="text-gray-600 mb-6 leading-relaxed">
                  Experience the power of {selectedFeature.title.toLowerCase()} with our advanced implementation
                  that provides real-time insights and actionable recommendations.
                </p>

                {/* Interactive metrics */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  {selectedFeature.stats.map((stat, index) => (
                    <motion.div
                      key={stat}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.2 }}
                      whileHover={{ scale: 1.05, y: -2 }}
                      className="text-center p-3 bg-gray-50 rounded-lg cursor-pointer"
                    >
                      <motion.div
                        className="text-lg font-bold text-primary-600 mb-1"
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{ duration: 2, repeat: Infinity, delay: index * 0.5 }}
                      >
                        {stat.split(' ')[0]}
                      </motion.div>
                      <div className="text-xs text-gray-600">
                        {stat.split(' ').slice(1).join(' ')}
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* CTA */}
                <motion.div
                  className="flex items-center justify-between pt-6 border-t border-gray-200"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8 }}
                >
                  <div className="flex items-center space-x-2">
                    <Globe className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-500">Available in all plans</span>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05, x: 4 }}
                    whileTap={{ scale: 0.95 }}
                    className="text-primary-600 font-medium text-sm hover:text-primary-700 transition-colors flex items-center gap-1"
                    onClick={() => {
                      document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                  >
                    Try it live
                    <ChevronRight className="w-4 h-4" />
                  </motion.button>
                </motion.div>
              </Card>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};