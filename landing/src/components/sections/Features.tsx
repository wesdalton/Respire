import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Brain, BarChart3, Sparkles, Database, Code } from 'lucide-react';

const features = [
  {
    icon: Activity,
    title: 'WHOOP API Integration',
    description: 'OAuth 2.0 flow to fetch daily health metrics: recovery, HRV, sleep, and strain data.',
  },
  {
    icon: Brain,
    title: 'Burnout Risk Algorithm',
    description: 'Multi-factor scoring system weighting recovery (25%), mood (30%), HRV (15%), sleep (15%), and strain (15%).',
  },
  {
    icon: BarChart3,
    title: 'Interactive Visualizations',
    description: 'Plotly charts for health trends, correlation heatmaps, and Apple-inspired dashboard design.',
  },
  {
    icon: Sparkles,
    title: 'AI-Powered Insights',
    description: 'OpenAI API integration for personalized, context-aware recommendations based on your data.',
  },
  {
    icon: Database,
    title: 'Cloud Architecture',
    description: 'Supabase backend with PostgreSQL database, secure authentication, and SQLite fallback.',
  },
  {
    icon: Code,
    title: 'Flask Blueprint Structure',
    description: 'Clean architecture with service layer pattern, modular code, and responsive Bootstrap UI.',
  },
];

export const Features: React.FC = () => {
  return (
    <section className="py-24 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Technical Implementation
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            A full-stack project demonstrating API integration, data analysis, cloud deployment, and thoughtful design.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="p-6 rounded-xl border border-gray-200 hover:border-blue-200 hover:shadow-lg transition-all"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};