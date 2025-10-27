import { usePageTitle } from '../hooks/usePageTitle';

export default function TermsOfService() {
  usePageTitle('Terms of Service');

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-sm p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
        <p className="text-sm text-gray-600 mb-8">Last Updated: October 27, 2025</p>

        <div className="prose prose-gray max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Agreement to Terms</h2>
            <p className="text-gray-700 leading-relaxed">
              By accessing or using Respire ("Service," "Platform," "we," "us," or "our"), available at tryrespire.ai, you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not access or use the Service.
            </p>
            <p className="text-gray-700 leading-relaxed">
              These Terms constitute a legally binding agreement between you and Wes Dalton, the creator and operator of Respire.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Description of Service</h2>
            <p className="text-gray-700 leading-relaxed">
              Respire is an AI-powered burnout prevention platform that:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Integrates with wearable health devices (WHOOP, Oura Ring) to collect health and biometric data</li>
              <li>Analyzes recovery scores, heart rate variability (HRV), sleep patterns, and activity levels</li>
              <li>Calculates personalized burnout risk scores using proprietary algorithms</li>
              <li>Provides AI-generated insights and recommendations via OpenAI's GPT-4</li>
              <li>Tracks mood ratings and health trends over time</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              <strong>Important:</strong> Respire is a wellness and productivity tool, NOT a medical device or healthcare service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. Eligibility</h2>
            <p className="text-gray-700 leading-relaxed">
              You must be at least 18 years old to use Respire. By using the Service, you represent and warrant that you meet this age requirement.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Account Registration and Security</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.1 Account Creation</h3>
            <p className="text-gray-700 leading-relaxed">
              To use Respire, you must create an account with a valid email address and password. You agree to:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Provide accurate and complete information</li>
              <li>Maintain the security of your password</li>
              <li>Notify us immediately of unauthorized access</li>
              <li>Accept responsibility for all activities under your account</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.2 Third-Party Integrations</h3>
            <p className="text-gray-700 leading-relaxed">
              Connecting WHOOP or Oura Ring accounts requires OAuth authorization. You grant Respire permission to access health data as specified during the OAuth flow. You may revoke this access at any time through your account settings.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Acceptable Use</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.1 Permitted Use</h3>
            <p className="text-gray-700 leading-relaxed">
              You may use Respire for personal wellness and burnout prevention purposes.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.2 Prohibited Activities</h3>
            <p className="text-gray-700 leading-relaxed">
              You agree NOT to:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Violate any laws or regulations</li>
              <li>Impersonate others or provide false information</li>
              <li>Attempt to gain unauthorized access to our systems</li>
              <li>Reverse engineer, decompile, or extract source code</li>
              <li>Use automated systems (bots, scrapers) without permission</li>
              <li>Interfere with or disrupt the Service</li>
              <li>Upload malicious code or viruses</li>
              <li>Share your account credentials with others</li>
              <li>Use the Service for medical diagnosis or treatment decisions</li>
              <li>Resell or redistribute access to the Service</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Medical Disclaimer</h2>
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 my-6">
              <p className="text-gray-900 font-semibold mb-2">IMPORTANT DISCLAIMER:</p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li><strong>Not Medical Advice:</strong> Respire is NOT a medical device and does not provide medical advice, diagnosis, or treatment</li>
                <li><strong>Not a Substitute:</strong> Our insights do NOT replace professional medical advice from qualified healthcare providers</li>
                <li><strong>Wellness Only:</strong> Respire is for wellness, fitness, and productivity tracking purposes only</li>
                <li><strong>Emergency:</strong> If you experience a medical emergency or mental health crisis, contact 911 or your local emergency services immediately</li>
                <li><strong>Consult Professionals:</strong> Always consult with licensed healthcare professionals before making health decisions</li>
                <li><strong>No Guarantee:</strong> We make no guarantees about preventing burnout, improving health, or any specific outcomes</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Intellectual Property</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">7.1 Our Property</h3>
            <p className="text-gray-700 leading-relaxed">
              Respire and its original content, features, algorithms, and functionality are owned by Wes Dalton and protected by international copyright, trademark, and intellectual property laws.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">7.2 Your Data</h3>
            <p className="text-gray-700 leading-relaxed">
              You retain ownership of your personal data and health information. By using Respire, you grant us a limited license to process and analyze your data to provide the Service as described in our Privacy Policy.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">7.3 Feedback</h3>
            <p className="text-gray-700 leading-relaxed">
              Any feedback, suggestions, or ideas you provide may be used by Respire without compensation or attribution.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">8. Payment and Subscriptions</h2>
            <p className="text-gray-700 leading-relaxed">
              Respire currently operates on a free-to-use basis. If we introduce paid features or subscriptions in the future:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Pricing will be clearly displayed before purchase</li>
              <li>You will be notified of changes to pricing or billing</li>
              <li>Refunds will be subject to our refund policy</li>
              <li>You may cancel subscriptions at any time</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">9. Third-Party Services</h2>
            <p className="text-gray-700 leading-relaxed">
              Respire integrates with third-party services (WHOOP, Oura, OpenAI, Supabase). Your use of these services is subject to their respective terms and privacy policies. We are not responsible for:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Third-party service availability or reliability</li>
              <li>Accuracy of data from third-party devices</li>
              <li>Changes to third-party APIs or pricing</li>
              <li>Third-party privacy practices (see our Privacy Policy)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">10. Disclaimer of Warranties</h2>
            <p className="text-gray-700 leading-relaxed">
              THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT</li>
              <li>ACCURACY, RELIABILITY, OR AVAILABILITY</li>
              <li>SECURITY OR VIRUS-FREE OPERATION</li>
              <li>UNINTERRUPTED OR ERROR-FREE SERVICE</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              We do not warrant that:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>The Service will meet your requirements</li>
              <li>Burnout prevention will be successful</li>
              <li>AI insights will be accurate or appropriate for your situation</li>
              <li>Data from wearable devices is accurate or complete</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">11. Limitation of Liability</h2>
            <p className="text-gray-700 leading-relaxed">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, RESPIRE AND WES DALTON SHALL NOT BE LIABLE FOR ANY:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES</li>
              <li>LOSS OF PROFITS, REVENUE, DATA, OR BUSINESS OPPORTUNITIES</li>
              <li>HEALTH ISSUES, INJURIES, OR MEDICAL CONDITIONS</li>
              <li>DECISIONS MADE BASED ON THE SERVICE'S INSIGHTS</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID TO RESPIRE IN THE PAST 12 MONTHS, OR $100 IF NO PAYMENT WAS MADE.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">12. Indemnification</h2>
            <p className="text-gray-700 leading-relaxed">
              You agree to indemnify, defend, and hold harmless Respire and Wes Dalton from any claims, damages, losses, liabilities, and expenses (including legal fees) arising from:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Your use or misuse of the Service</li>
              <li>Violation of these Terms</li>
              <li>Violation of any third-party rights</li>
              <li>Your health decisions or outcomes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">13. Termination</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">13.1 By You</h3>
            <p className="text-gray-700 leading-relaxed">
              You may delete your account at any time through Settings or by contacting us at support@tryrespire.ai
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">13.2 By Us</h3>
            <p className="text-gray-700 leading-relaxed">
              We may suspend or terminate your account if you:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Violate these Terms</li>
              <li>Engage in fraudulent or illegal activity</li>
              <li>Abuse or threaten other users or staff</li>
              <li>Create multiple accounts or evade bans</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">13.3 Effect of Termination</h3>
            <p className="text-gray-700 leading-relaxed">
              Upon termination, your access to the Service will cease immediately. Your data will be deleted in accordance with our Privacy Policy (typically within 30 days).
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">14. Changes to Terms</h2>
            <p className="text-gray-700 leading-relaxed">
              We reserve the right to modify these Terms at any time. We will notify you of material changes via:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Email notification</li>
              <li>In-app notification</li>
              <li>Updated "Last Updated" date on this page</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              Your continued use of Respire after changes constitutes acceptance of the modified Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">15. Governing Law and Disputes</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">15.1 Governing Law</h3>
            <p className="text-gray-700 leading-relaxed">
              These Terms are governed by the laws of the Commonwealth of Pennsylvania and the United States, without regard to conflict of law principles.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">15.2 Dispute Resolution</h3>
            <p className="text-gray-700 leading-relaxed">
              Any disputes will be resolved through:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Informal negotiation (contact us first at legal@tryrespire.ai)</li>
              <li>Binding arbitration if negotiation fails</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">15.3 Class Action Waiver</h3>
            <p className="text-gray-700 leading-relaxed">
              You agree to resolve disputes individually and waive the right to participate in class actions or representative proceedings.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">16. General Provisions</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">16.1 Entire Agreement</h3>
            <p className="text-gray-700 leading-relaxed">
              These Terms, along with our Privacy Policy, constitute the entire agreement between you and Respire.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">16.2 Severability</h3>
            <p className="text-gray-700 leading-relaxed">
              If any provision is found unenforceable, the remaining provisions will continue in full force.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">16.3 Waiver</h3>
            <p className="text-gray-700 leading-relaxed">
              Our failure to enforce any right or provision does not constitute a waiver of that right.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">16.4 Assignment</h3>
            <p className="text-gray-700 leading-relaxed">
              You may not assign these Terms without our consent. We may assign these Terms without restriction.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">17. Contact Information</h2>
            <p className="text-gray-700 leading-relaxed">
              For questions about these Terms of Service:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg mt-4">
              <p className="text-gray-700"><strong>Respire</strong></p>
              <p className="text-gray-700">Wes Dalton, Founder</p>
              <p className="text-gray-700">University of Pennsylvania '27</p>
              <p className="text-gray-700">Email: <a href="mailto:legal@tryrespire.ai" className="text-blue-600 hover:underline">legal@tryrespire.ai</a></p>
              <p className="text-gray-700">Support: <a href="mailto:support@tryrespire.ai" className="text-blue-600 hover:underline">support@tryrespire.ai</a></p>
              <p className="text-gray-700">Website: <a href="https://tryrespire.ai" className="text-blue-600 hover:underline">tryrespire.ai</a></p>
            </div>
          </section>

          <section className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600 italic">
              By clicking "Sign Up" or "I Agree" when creating your account, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service and our Privacy Policy.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}