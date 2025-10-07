import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Hero } from './components/sections/Hero';
import { Features } from './components/sections/Features';
import { About } from './components/sections/About';
import { Footer } from './components/layout/Footer';

function App() {
  return (
    <div className="min-h-screen bg-white">
      <Helmet>
        <title>Respire - Burnout Prevention Dashboard</title>
        <meta
          name="description"
          content="A passion project combining WHOOP data, machine learning, and interactive visualizations to predict burnout risk."
        />
      </Helmet>

      <main>
        <Hero />
        <Features />
        <About />
      </main>

      <Footer />
    </div>
  );
}

export default App;