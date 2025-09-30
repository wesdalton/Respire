import React from 'react';
import { motion } from 'framer-motion';
import { Github, ExternalLink } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-green-50 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-6">
            <span>A passion project by Wes Dalton • UPenn '26</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
            Prevent Burnout
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
              Before It Happens
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Combining WHOOP data, multi-factor analysis, and AI insights to predict burnout risk
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <a
              href="http://127.0.0.1:3000"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors w-full sm:w-auto justify-center"
            >
              <ExternalLink className="w-5 h-5" />
              View Live Dashboard
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-gray-900 border-2 border-gray-300 rounded-lg font-semibold hover:border-gray-400 transition-colors w-full sm:w-auto justify-center"
            >
              <Github className="w-5 h-5" />
              View on GitHub
            </a>
          </div>

          {/* Tech Stack */}
          <div className="space-y-2">
            <p className="text-sm text-gray-500 font-medium">Built with</p>
            <div className="flex flex-wrap items-center justify-center gap-4 text-gray-600">
              <span className="text-sm font-medium">Python</span>
              <span className="text-gray-300">•</span>
              <span className="text-sm font-medium">Flask</span>
              <span className="text-gray-300">•</span>
              <span className="text-sm font-medium">WHOOP API</span>
              <span className="text-gray-300">•</span>
              <span className="text-sm font-medium">Supabase</span>
              <span className="text-gray-300">•</span>
              <span className="text-sm font-medium">Plotly</span>
              <span className="text-gray-300">•</span>
              <span className="text-sm font-medium">OpenAI</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};