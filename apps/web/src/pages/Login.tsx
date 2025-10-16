import { LoginForm } from '../components/auth/LoginForm';
import { usePageTitle } from '../hooks/usePageTitle';

export default function Login() {
  usePageTitle('Sign In');
  return <LoginForm />;
}
