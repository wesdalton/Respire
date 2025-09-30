import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, Shield, Crown, ArrowRight, Users, Building } from 'lucide-react';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';
import { pricingTiers } from '../../data/mockData';

export const Pricing: React.FC = () => {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly');

  const getPrice = (basePrice: number) => {
    if (basePrice === 0) return 'Custom';
    return billingPeriod === 'annual'
      ? Math.round(basePrice * 0.8) // 20% discount for annual
      : basePrice;
  };

  const getSavings = (basePrice: number) => {
    if (basePrice === 0) return null;
    return billingPeriod === 'annual' ? Math.round(basePrice * 0.2 * 12) : null;
  };

  return (
    <section id="pricing" className="section-padding bg-gradient-to-br from-gray-50 via-white to-primary-50">
      <div className="container-max">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-center mb-16"
        >
          <Badge variant="primary" size="lg" className="mb-4">
            Simple Pricing
          </Badge>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            <span className="text-gradient">Choose your plan</span>
            <br />
            and start preventing burnout
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Transparent pricing with no hidden fees. Start with a free trial
            and scale as your team grows.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-12">
            <span className={`text-sm font-medium ${billingPeriod === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Monthly
            </span>
            <motion.button
              onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
              className={`relative w-14 h-7 rounded-full transition-colors duration-200 ${
                billingPeriod === 'annual' ? 'bg-primary-600' : 'bg-gray-200'
              }`}
            >
              <motion.div
                animate={{ x: billingPeriod === 'annual' ? 28 : 4 }}
                transition={{ duration: 0.2 }}
                className="absolute top-1 w-5 h-5 bg-white rounded-full shadow-sm"
              />
            </motion.button>
            <div className="flex items-center space-x-2">
              <span className={`text-sm font-medium ${billingPeriod === 'annual' ? 'text-gray-900' : 'text-gray-500'}`}>
                Annual
              </span>
              <Badge variant="success" size="sm">Save 20%</Badge>
            </div>
          </div>
        </motion.div>

        {/* Pricing Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          {pricingTiers.map((tier, index) => {
            const price = getPrice(tier.price);
            const savings = getSavings(tier.price);
            const isPopular = tier.highlighted;
            const Icon = tier.id === 'individual' ? Users :
                        tier.id === 'team' ? Building : Crown;

            return (
              <motion.div
                key={tier.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`relative ${isPopular ? 'lg:scale-105' : ''}`}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge variant="primary" size="lg" className="px-4 py-2">
                      <Crown className="w-4 h-4 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}

                <Card
                  className={`h-full p-8 text-center relative ${
                    isPopular
                      ? 'border-primary-300 bg-gradient-to-b from-primary-50 to-white shadow-xl'
                      : ''
                  }`}
                  hover
                >
                  {/* Plan Icon */}
                  <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center ${
                    isPopular
                      ? 'bg-primary-100'
                      : 'bg-gray-100'
                  }`}>
                    <Icon className={`w-8 h-8 ${
                      isPopular ? 'text-primary-600' : 'text-gray-600'
                    }`} />
                  </div>

                  {/* Plan Name */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {tier.name}
                  </h3>

                  {/* Plan Description */}
                  <p className="text-gray-600 mb-6 min-h-[3rem]">
                    {tier.description}
                  </p>

                  {/* Price */}
                  <div className="mb-8">
                    <div className="flex items-baseline justify-center space-x-2">
                      <span className="text-5xl font-bold text-gray-900">
                        {typeof price === 'number' ? `$${price}` : price}
                      </span>
                      {typeof price === 'number' && (
                        <span className="text-gray-500">/{tier.period}</span>
                      )}
                    </div>
                    {savings && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-success-600 text-sm font-medium mt-2"
                      >
                        Save ${savings}/year
                      </motion.div>
                    )}
                  </div>

                  {/* Features */}
                  <ul className="space-y-4 mb-8 text-left">
                    {tier.features.map((feature, featureIndex) => (
                      <motion.li
                        key={featureIndex}
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: featureIndex * 0.1 }}
                        className="flex items-start space-x-3"
                      >
                        <Check className="w-5 h-5 text-success-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700">{feature}</span>
                      </motion.li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <Button
                    variant={isPopular ? 'primary' : 'outline'}
                    size="lg"
                    className="w-full"
                    icon={ArrowRight}
                    iconPosition="right"
                  >
                    {tier.cta}
                  </Button>

                  {tier.id === 'individual' && (
                    <p className="text-sm text-gray-500 mt-3">
                      14-day free trial • No credit card required
                    </p>
                  )}
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Enterprise Features */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <Card className="p-8 bg-gradient-to-r from-gray-900 to-gray-800 text-white">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <div className="flex items-center space-x-3 mb-4">
                  <Shield className="w-8 h-8 text-warning-400" />
                  <h3 className="text-2xl font-bold">Enterprise Security & Compliance</h3>
                </div>
                <p className="text-gray-300 mb-6 leading-relaxed">
                  Advanced security features and compliance capabilities for organizations
                  with strict regulatory requirements.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <Check className="w-4 h-4 text-success-400" />
                    <span className="text-sm text-gray-300">SOC 2 Type II</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Check className="w-4 h-4 text-success-400" />
                    <span className="text-sm text-gray-300">HIPAA Compliant</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Check className="w-4 h-4 text-success-400" />
                    <span className="text-sm text-gray-300">GDPR Ready</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Check className="w-4 h-4 text-success-400" />
                    <span className="text-sm text-gray-300">SSO/SAML</span>
                  </div>
                </div>
              </div>
              <div className="text-center lg:text-right">
                <Button
                  variant="secondary"
                  size="lg"
                  className="bg-white hover:bg-gray-50 text-gray-900"
                >
                  Schedule Security Review
                </Button>
                <p className="text-gray-400 text-sm mt-3">
                  Custom pricing based on requirements
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* FAQ Preview */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-center mb-16"
        >
          <h3 className="text-2xl font-bold text-gray-900 mb-8">
            Frequently asked questions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto text-left">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Can I switch plans anytime?
              </h4>
              <p className="text-gray-600 text-sm">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                What wearables are supported?
              </h4>
              <p className="text-gray-600 text-sm">
                We support 15+ devices including WHOOP, Oura, Apple Watch, Fitbit, Garmin, and more.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Is my data secure?
              </h4>
              <p className="text-gray-600 text-sm">
                Absolutely. We use bank-level encryption and are SOC 2 and HIPAA compliant.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Do you offer refunds?
              </h4>
              <p className="text-gray-600 text-sm">
                Yes, we offer a 30-day money-back guarantee for all paid plans, no questions asked.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Final CTA */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center"
        >
          <Card className="bg-gradient-to-r from-primary-600 to-success-600 border-0 p-8 text-white max-w-3xl mx-auto">
            <Zap className="w-12 h-12 mx-auto mb-4 text-warning-300" />
            <h3 className="text-2xl sm:text-3xl font-bold mb-4">
              Ready to prevent burnout?
            </h3>
            <p className="text-primary-100 mb-6 text-lg">
              Join thousands of professionals who've transformed their relationship with work.
              Start your free trial today.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
              <Button
                variant="secondary"
                size="lg"
                className="bg-white hover:bg-gray-50 text-primary-600"
              >
                Start 14-Day Free Trial
              </Button>
              <div className="text-primary-100 text-sm">
                No credit card required • Cancel anytime
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  );
};