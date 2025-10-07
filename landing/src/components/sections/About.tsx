import React from 'react';
import { motion } from 'framer-motion';
import { Linkedin, Mail, Github } from 'lucide-react';

export const About: React.FC = () => {
  return (
    <section className="py-24 px-4 bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About This Project
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Built by Wes Dalton, a Computer Science student at UPenn '26, as a passion project
            to explore the intersection of health data, machine learning, and preventive wellness.
          </p>

          {/* What I Learned */}
          <div className="bg-white rounded-xl border border-gray-200 p-8 mb-8 text-left">
            <h3 className="text-2xl font-semibold text-gray-900 mb-4">What I Learned</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>OAuth 2.0 implementation with third-party APIs (WHOOP)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>Database design and cloud deployment with Supabase</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>Data analysis and visualization with Pandas, NumPy, and Plotly</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>AI API integration for generating personalized insights</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>Flask Blueprint architecture and modular code design</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>User authentication, session management, and security best practices</span>
              </li>
            </ul>
          </div>

          {/* Project Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-3xl font-bold text-blue-600 mb-1">~2,000</div>
              <div className="text-sm text-gray-600">Lines of Code</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-3xl font-bold text-green-600 mb-1">20+</div>
              <div className="text-sm text-gray-600">Health Metrics</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-3xl font-bold text-purple-600 mb-1">6</div>
              <div className="text-sm text-gray-600">Technologies</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-3xl font-bold text-orange-600 mb-1">Full</div>
              <div className="text-sm text-gray-600">Stack Project</div>
            </div>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Get in Touch</h3>
            <p className="text-gray-600 mb-6">
              Interested in discussing this project or exploring opportunities? Let's connect.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                <Linkedin className="w-5 h-5" />
                LinkedIn
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors"
              >
                <Github className="w-5 h-5" />
                GitHub
              </a>
              <a
                href="mailto:your.email@upenn.edu"
                className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 border-2 border-gray-300 rounded-lg font-semibold hover:border-gray-400 transition-colors"
              >
                <Mail className="w-5 h-5" />
                Email
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};