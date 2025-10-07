import React from 'react';
import { motion } from 'framer-motion';
import { Star, Quote, TrendingUp, Users } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { testimonials, trustedCompanies } from '../../data/mockData';

export const SocialProof: React.FC = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 }
    }
  };

  return (
    <section className="section-padding bg-white">
      <div className="container-max">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-center mb-16"
        >
          <Badge variant="success" size="lg" className="mb-4 inline-flex items-center gap-2">
            <Users className="w-4 h-4" />
            Trusted Worldwide
          </Badge>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Join <span className="text-gradient">500+ teams</span>
            <br />
            already preventing burnout
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From Fortune 500 companies to fast-growing startups, teams worldwide trust
            Respire to protect their most valuable asset: their people.
          </p>
        </motion.div>

        {/* Company Logos */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          className="mb-20"
        >
          <motion.p
            variants={itemVariants}
            className="text-center text-sm text-gray-500 font-medium mb-8"
          >
            Trusted by high-performing teams at
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 items-center opacity-60 hover:opacity-100 transition-opacity duration-300"
          >
            {trustedCompanies.map((company) => (
              <motion.div
                key={company.id}
                whileHover={{ scale: 1.1, opacity: 1 }}
                className="flex items-center justify-center h-16 grayscale hover:grayscale-0 transition-all duration-300"
              >
                {/* Placeholder for company logos */}
                <div className="text-2xl font-bold text-gray-400 hover:text-gray-700 transition-colors">
                  {company.name}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Testimonials Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16"
        >
          {testimonials.map((testimonial, index) => (
            <motion.div key={testimonial.id} variants={itemVariants}>
              <Card hover className="h-full p-6 relative">
                {/* Quote Icon */}
                <div className="absolute -top-4 left-6">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <Quote className="w-4 h-4 text-primary-600" />
                  </div>
                </div>

                {/* Rating */}
                <div className="flex items-center space-x-1 mb-4 pt-2">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-warning-400 fill-current" />
                  ))}
                </div>

                {/* Quote */}
                <blockquote className="text-gray-700 mb-6 italic leading-relaxed">
                  "{testimonial.quote}"
                </blockquote>

                {/* Metrics */}
                {testimonial.metrics && (
                  <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                    {testimonial.metrics.map((metric) => (
                      <div key={metric.label} className="text-center">
                        <div className="text-2xl font-bold text-primary-600 mb-1">
                          {metric.value}
                        </div>
                        <div className="text-xs text-gray-500">{metric.label}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Author */}
                <div className="flex items-center space-x-3 border-t border-gray-200 pt-4">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                  <div>
                    <div className="font-semibold text-gray-900 text-sm">
                      {testimonial.name}
                    </div>
                    <div className="text-gray-500 text-sm">
                      {testimonial.title} at {testimonial.company}
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-8 sm:p-12 text-white text-center"
        >
          <h3 className="text-2xl sm:text-3xl font-bold mb-4">
            The numbers speak for themselves
          </h3>
          <p className="text-primary-100 mb-8 text-lg max-w-2xl mx-auto">
            Our platform has helped thousands of professionals and hundreds of teams
            achieve better work-life balance and sustainable performance.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center"
            >
              <div className="text-4xl sm:text-5xl font-bold mb-2">67%</div>
              <div className="text-primary-100">Average burnout reduction</div>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center"
            >
              <div className="text-4xl sm:text-5xl font-bold mb-2">94%</div>
              <div className="text-primary-100">Prediction accuracy</div>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center"
            >
              <div className="text-4xl sm:text-5xl font-bold mb-2">10k+</div>
              <div className="text-primary-100">Professionals protected</div>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center"
            >
              <div className="text-4xl sm:text-5xl font-bold mb-2">300%</div>
              <div className="text-primary-100">Average ROI</div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            className="mt-8 pt-8 border-t border-primary-500"
          >
            <div className="flex items-center justify-center space-x-4 text-primary-100">
              <TrendingUp className="w-5 h-5" />
              <span className="text-sm font-medium">
                95% of teams report improved well-being within 30 days
              </span>
            </div>
          </motion.div>
        </motion.div>

        {/* Case Study CTA */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-center mt-16"
        >
          <Card className="bg-gradient-to-r from-success-50 to-primary-50 border-0 p-8 max-w-3xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Want to see detailed case studies?
            </h3>
            <p className="text-gray-600 mb-6">
              Learn how companies like yours achieved measurable improvements in
              employee well-being and reduced turnover by up to 45%.
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-primary"
            >
              Download Case Studies
            </motion.button>
          </Card>
        </motion.div>
      </div>
    </section>
  );
};