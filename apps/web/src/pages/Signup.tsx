import { SignupForm } from '../components/auth/SignupForm';
import { usePageTitle } from '../hooks/usePageTitle';

export default function Signup() {
  usePageTitle('Sign Up');
  return <SignupForm />;
}
