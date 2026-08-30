import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Layout from './components/Layout';
import { About, Assistant, Auth, Details, HowItWorks, Landing, NotFound, Profile, Directory } from './pages/Pages';
import { currentUser, logout as endSession } from './api/client';

function ProtectedRoute({ user, children }) {
  const location = useLocation();
  return user ? children : <Navigate to="/login" replace state={{ from: location.pathname }} />;
}

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const nav = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('govassist-access-token')) {
      setChecking(false);
      return;
    }
    currentUser()
      .then(setUser)
      .catch(() => localStorage.removeItem('govassist-access-token'))
      .finally(() => setChecking(false));
  }, []);

  const authenticated = (session) => {
    localStorage.setItem('govassist-access-token', session.access_token);
    setUser(session.user);
  };

  const signOut = async () => {
    try {
      await endSession();
    } catch {}
    localStorage.removeItem('govassist-access-token');
    setUser(null);
    nav('/login');
  };

  if (checking) {
    return (
      <Layout user={null}>
        <section className="shell py-16">Checking your session…</section>
      </Layout>
    );
  }

  return (
    <Layout user={user} onLogout={signOut}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/schemes" element={<Directory />} />
        <Route path="/scheme/:schemeId" element={<Details />} />
        <Route path="/profile" element={<ProtectedRoute user={user}><Profile user={user} /></ProtectedRoute>} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/about" element={<About />} />
        <Route path="/login" element={user ? <Navigate to="/assistant" replace /> : <Auth onAuthenticated={authenticated} />} />
        <Route path="/register" element={user ? <Navigate to="/assistant" replace /> : <Auth register onAuthenticated={authenticated} />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}
