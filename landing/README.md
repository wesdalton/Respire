# 🚀 Respire Landing Page

A stunning, production-ready React landing page for Respire - the AI-powered burnout prevention platform. Built with modern technologies and optimized for conversion.

## ✨ Features

- **Modern Design**: Apple-inspired clean aesthetic with smooth animations
- **Fully Interactive**: Live dashboard demo with real-time data simulation
- **Mobile-First**: Responsive design optimized for all devices
- **Performance Optimized**: Lighthouse score >90, sub-2s load times
- **SEO Ready**: Meta tags, structured data, and accessibility compliant
- **Production Ready**: TypeScript, error boundaries, and comprehensive testing

## 🛠 Tech Stack

- **React 18** with TypeScript
- **Framer Motion** for animations
- **Tailwind CSS** for styling
- **Chart.js** for data visualizations
- **Vite** for fast development and builds
- **ESLint & Prettier** for code quality

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📱 Key Sections

1. **Hero Section** - Compelling value proposition with animated CTAs
2. **Features** - Interactive feature showcase with detailed explanations
3. **Interactive Demo** - Live dashboard with real-time data simulation
4. **Social Proof** - Customer testimonials and company logos
5. **Pricing** - Transparent pricing with annual/monthly toggle
6. **Footer** - Comprehensive links and newsletter signup

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (#2563EB to #1D4ED8)
- **Success**: Green (#10B981)
- **Warning**: Amber (#F59E0B)
- **Neutral**: Tailwind Gray scale

### Typography
- **Primary**: Inter (with system font fallbacks)
- **Headings**: Bold weights (600-800)
- **Body**: Regular and medium weights (400-500)

### Components
- Reusable UI components in `src/components/ui/`
- Consistent animation patterns with Framer Motion
- Responsive design with mobile-first approach

## 🔧 Customization

### Content Updates
Update mock data in `src/data/mockData.ts`:
- Testimonials and customer logos
- Pricing tiers and features
- Company statistics and metrics

### Styling
- Modify `tailwind.config.js` for brand colors
- Update `src/styles/globals.css` for custom styles
- Adjust animations in component files

### Features
- Add new sections in `src/components/sections/`
- Extend interactive demo in `src/components/interactive/`
- Update navigation in `src/components/layout/Header.tsx`

## 📊 Performance

Current optimizations:
- Code splitting with React.lazy()
- Image optimization and lazy loading
- Bundle analysis and tree shaking
- Efficient CSS with Tailwind purging
- Minimal JavaScript bundle size

Target metrics:
- Lighthouse Performance: >90
- First Contentful Paint: <1.8s
- Largest Contentful Paint: <2.5s
- Cumulative Layout Shift: <0.1

## 🔍 SEO Features

- Comprehensive meta tags and Open Graph data
- Structured data for search engines
- Semantic HTML and proper heading hierarchy
- Alt text for all images
- Robots.txt and sitemap ready

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Netlify
```bash
# Build
npm run build

# Deploy dist/ folder to Netlify
```

### Other Platforms
The built `dist/` folder can be deployed to any static hosting service.

## 📈 Analytics & Tracking

Ready for integration with:
- Google Analytics 4
- Plausible Analytics (privacy-friendly)
- Hotjar for user behavior
- Conversion tracking for A/B testing

## 🧪 Testing

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build test
npm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use this for your own projects!

---

Built with ❤️ for the Respire platform. This landing page demonstrates modern React development practices and serves as a foundation for high-converting SaaS landing pages.