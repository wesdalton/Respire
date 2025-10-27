import { usePageTitle } from '../hooks/usePageTitle';

export default function Privacy() {
  usePageTitle('Privacy Policy');

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-sm p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
        <p className="text-sm text-gray-600 mb-8">Last Updated: October 27, 2025</p>

        <div className="prose prose-gray max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Introduction</h2>
            <p className="text-gray-700 leading-relaxed">
              Welcome to Respire ("we," "our," or "us"). Respire is an AI-powered burnout prevention platform that integrates with wearable health devices (WHOOP, Oura Ring) to provide personalized insights. We are committed to protecting your privacy and handling your data with care and transparency.
            </p>
            <p className="text-gray-700 leading-relaxed">
              This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our service at tryrespire.ai.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Information We Collect</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.1 Account Information</h3>
            <p className="text-gray-700 leading-relaxed">
              When you create an account, we collect:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Email address</li>
              <li>Name (optional)</li>
              <li>Password (encrypted and never stored in plain text)</li>
              <li>Account preferences and settings</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.2 Health and Biometric Data</h3>
            <p className="text-gray-700 leading-relaxed">
              With your explicit consent through OAuth connections, we collect health data from connected devices:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>WHOOP:</strong> Recovery score, heart rate variability (HRV), resting heart rate, sleep duration and quality, strain score, workout data</li>
              <li><strong>Oura Ring:</strong> Readiness score, sleep metrics, activity scores, heart rate data, body temperature</li>
              <li><strong>Manual entries:</strong> Mood ratings, personal notes</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.3 Usage Information</h3>
            <p className="text-gray-700 leading-relaxed">
              We automatically collect:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Log data (IP address, browser type, access times)</li>
              <li>Device information</li>
              <li>Feature usage patterns</li>
              <li>Error reports and performance data</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-700 leading-relaxed">
              We use your information to:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>Provide Core Services:</strong> Calculate burnout risk scores, generate personalized health insights, track health trends</li>
              <li><strong>AI Analysis:</strong> Use OpenAI's GPT-4 to analyze your health data and provide recommendations (your data is sent to OpenAI's API with encryption)</li>
              <li><strong>Sync Data:</strong> Maintain connections with WHOOP and Oura Ring to keep your data up-to-date</li>
              <li><strong>Improve Service:</strong> Analyze usage patterns to enhance features and user experience</li>
              <li><strong>Communication:</strong> Send important updates, notifications, and support responses</li>
              <li><strong>Security:</strong> Detect and prevent fraud, abuse, and security incidents</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Data Sharing and Disclosure</h2>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.1 Third-Party Services</h3>
            <p className="text-gray-700 leading-relaxed">
              We share data with trusted service providers:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>Supabase:</strong> Database and authentication (encrypted storage)</li>
              <li><strong>OpenAI:</strong> AI insights generation (health data is processed but not stored by OpenAI for training)</li>
              <li><strong>Railway/Vercel:</strong> Hosting infrastructure</li>
              <li><strong>WHOOP/Oura:</strong> Health data retrieval via OAuth</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.2 Anonymous Data</h3>
            <p className="text-gray-700 leading-relaxed">
              With your consent (opt-in only), we may use anonymized, aggregated data for research and improving burnout prevention algorithms. This data cannot identify you personally.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.3 Legal Requirements</h3>
            <p className="text-gray-700 leading-relaxed">
              We may disclose your information if required by law, court order, or to protect the rights, property, or safety of Respire, our users, or others.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.4 What We Don't Do</h3>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>We do NOT sell your personal or health data</li>
              <li>We do NOT share your data with advertisers</li>
              <li>We do NOT use your data for marketing purposes without explicit consent</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Data Security</h2>
            <p className="text-gray-700 leading-relaxed">
              We implement industry-standard security measures:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Encryption in transit (HTTPS/TLS) and at rest</li>
              <li>Secure authentication via Supabase with JWT tokens</li>
              <li>OAuth tokens encrypted in database</li>
              <li>Regular security audits and updates</li>
              <li>Access controls and monitoring</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              However, no method of transmission over the Internet is 100% secure. While we strive to protect your data, we cannot guarantee absolute security.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Your Rights and Choices</h2>
            <p className="text-gray-700 leading-relaxed">
              You have the right to:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Correction:</strong> Update or correct your information</li>
              <li><strong>Deletion:</strong> Request deletion of your account and data</li>
              <li><strong>Export:</strong> Download your health data in a portable format</li>
              <li><strong>Disconnect:</strong> Revoke access to WHOOP or Oura at any time via Settings</li>
              <li><strong>Opt-out:</strong> Disable email notifications or data sharing preferences</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              To exercise these rights, contact us at <a href="mailto:privacy@tryrespire.ai" className="text-blue-600 hover:underline">privacy@tryrespire.ai</a>
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Data Retention</h2>
            <p className="text-gray-700 leading-relaxed">
              We retain your data for as long as your account is active or as needed to provide services. Upon account deletion:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Personal and health data is deleted within 30 days</li>
              <li>Anonymized usage statistics may be retained for analytics</li>
              <li>Legal and compliance records retained as required by law</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">8. Children's Privacy</h2>
            <p className="text-gray-700 leading-relaxed">
              Respire is not intended for users under 18. We do not knowingly collect data from children. If you believe we have collected information from a minor, please contact us immediately.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">9. International Users</h2>
            <p className="text-gray-700 leading-relaxed">
              Respire is operated in the United States. If you access our service from outside the US, your data may be transferred to and processed in the US. By using Respire, you consent to this transfer.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">10. Changes to This Policy</h2>
            <p className="text-gray-700 leading-relaxed">
              We may update this Privacy Policy periodically. We will notify you of significant changes via email or in-app notification. Continued use of Respire after changes constitutes acceptance.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">11. Contact Us</h2>
            <p className="text-gray-700 leading-relaxed">
              If you have questions or concerns about this Privacy Policy:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg mt-4">
              <p className="text-gray-700"><strong>Respire</strong></p>
              <p className="text-gray-700">Wes Dalton, Founder</p>
              <p className="text-gray-700">University of Pennsylvania '27</p>
              <p className="text-gray-700">Email: <a href="mailto:privacy@tryrespire.ai" className="text-blue-600 hover:underline">privacy@tryrespire.ai</a></p>
              <p className="text-gray-700">Website: <a href="https://tryrespire.ai" className="text-blue-600 hover:underline">tryrespire.ai</a></p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">12. HIPAA Disclaimer</h2>
            <p className="text-gray-700 leading-relaxed">
              Respire is a wellness application and is NOT a HIPAA-covered entity. The health data we collect is for wellness and burnout prevention purposes only. Respire is not a medical device and should not be used for diagnosis or treatment of medical conditions. Always consult with healthcare professionals for medical advice.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}