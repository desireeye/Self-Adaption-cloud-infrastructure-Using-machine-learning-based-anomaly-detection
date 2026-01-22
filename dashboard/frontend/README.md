# Self-Adaptive Dashboard Frontend Setup Guide

## 📋 Prerequisites

- Node.js 14+ and npm/yarn
- React 18+
- Modern web browser

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd dashboard/frontend
npm install
```

### 2. Set API URL (Optional)
Create `.env.local` file:
```env
REACT_APP_API_URL=http://localhost:8000
```

Default: `http://localhost:8000`

### 3. Start Development Server
```bash
npm start
```

Dashboard opens at `http://localhost:3000`

## 📊 Features

### Bento-Grid UI
- ✅ Modern, Apple-style card layout
- ✅ Responsive grid system
- ✅ Dark theme optimized
- ✅ Smooth animations and transitions

### Real-Time Monitoring
- **CPU Usage** - Live percentage with trend
- **Memory Usage** - Current utilization
- **Disk Usage** - Storage status
- **Network Throughput** - Sent/Received bytes per second
- **System Temperature** - Current system heat (if available)

### Anomaly Detection
- **Anomaly Level** - NORMAL/WARNING/CRITICAL/EMERGENCY
- **Anomaly Score** - 0-1 probability
- **Confidence** - Model confidence in prediction
- **Affected Metrics** - Which metrics triggered anomaly
- **Feature Importances** - Contributing factors

### System Health
- **Health Score** - 0-100 gauge
- **System Status** - STABLE/ADAPTING/RECOVERING/CRITICAL
- **Active Adaptations** - Currently executing actions
- **Anomalies/Hour** - Count of detected anomalies

### Adaptive Actions
- **Scale Up** - Add compute resources
- **Scale Down** - Remove compute resources
- **Clear Cache** - Free memory
- **Optimize CPU** - Improve scheduling
- **Recent Actions** - Timeline of executed actions

### ML Model Analytics
- **Accuracy** - Overall model correctness
- **Precision** - False positive rate
- **Recall** - False negative rate
- **Training Status** - Active training indicator

### Charts & Visualizations
- **Metrics Timeline** - 5-minute history of CPU/Memory/Disk
- **Anomaly Score Distribution** - Histogram of anomaly scores
- **Network Chart** - Sent/Received throughput over time
- **Actions Timeline** - Recent adaptive actions

## 🎨 Customization

### Colors & Styling
Edit `src/styles/globals.css`:
```css
.status-stable { @apply bg-green-500/20 text-green-400; }
.status-critical { @apply bg-red-500/20 text-red-400; }
```

### Theme
Modify `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: '#3b82f6',
      danger: '#ef4444',
    }
  }
}
```

### Update Intervals
In `src/pages/Dashboard.jsx`:
```javascript
const { metrics } = useMetrics(2000);        // 2 seconds
const { anomaly } = useAnomalyDetection(3000); // 3 seconds
const { health } = useSystemHealth(5000);    // 5 seconds
```

## 📦 Build for Production

### Create Production Build
```bash
npm run build
```

Creates optimized build in `build/` directory.

### Deploy to Static Hosting

#### Netlify
```bash
npm run build
# Drag & drop 'build' folder to Netlify
```

#### Vercel
```bash
npm install -g vercel
vercel
```

#### AWS S3 + CloudFront
```bash
npm run build
aws s3 sync build/ s3://your-bucket/
```

#### GitHub Pages
1. Add to `package.json`: `"homepage": "https://yourusername.github.io/dashboard"`
2. `npm run build`
3. `npx gh-pages -d build`

## 🔌 API Integration

### Connecting to Backend

The frontend automatically connects to the backend at `http://localhost:8000`.

To change API URL:

**Option 1: Environment Variable**
```bash
REACT_APP_API_URL=https://api.yourdomain.com npm start
```

**Option 2: .env.local File**
```env
REACT_APP_API_URL=https://api.yourdomain.com
```

**Option 3: Edit Hook**
```javascript
// src/hooks/useApi.js
const API_BASE_URL = 'https://api.yourdomain.com';
```

### API Error Handling

Frontend automatically handles:
- ✅ Connection errors
- ✅ Timeout errors
- ✅ Invalid responses
- ✅ Missing data

Errors display in components with retry buttons.

## 🧪 Testing

### Test with Mock Data
Create `src/hooks/useMockApi.js` for development:

```javascript
export const useMetrics = () => {
  return {
    metrics: { cpu_percent: 45, memory_percent: 62 },
    loading: false,
    error: null
  };
};
```

### Local Testing Checklist
- [ ] Backend running at `http://localhost:8000`
- [ ] API endpoints accessible with curl
- [ ] Dashboard loads without CORS errors
- [ ] Metrics update in real-time
- [ ] Anomaly detection working
- [ ] Actions trigger successfully
- [ ] Charts render correctly

## 📊 Component Structure

```
src/
├── components/
│   ├── MetricCards.jsx    # Metric display components
│   └── Charts.jsx         # Chart visualizations
├── hooks/
│   └── useApi.js          # API integration hooks
├── pages/
│   └── Dashboard.jsx      # Main dashboard page
├── styles/
│   └── globals.css        # Tailwind & custom styles
├── App.jsx                # Root component
└── index.jsx              # Entry point
```

## 🚀 Performance Tips

1. **Lazy Loading**: Load charts only when visible
2. **Memoization**: Use `React.memo()` for charts
3. **Debouncing**: Debounce rapid updates
4. **CDN**: Use CDN for static assets

```javascript
import { lazy, Suspense } from 'react';

const MetricsChart = lazy(() => import('./Charts'));

<Suspense fallback={<Skeleton />}>
  <MetricsChart />
</Suspense>
```

## 🔐 Security

1. **API URL**: Always use HTTPS in production
2. **CORS**: Backend handles with proper origins
3. **Authentication**: Add JWT if needed
4. **Sensitive Data**: Don't expose credentials in frontend

## 📱 Responsive Design

Dashboard is fully responsive:
- 📱 Mobile (320px+)
- 📱 Tablet (768px+)
- 💻 Desktop (1024px+)

Grid adjusts automatically based on screen size.

## 🆘 Troubleshooting

### CORS Errors
```javascript
// Ensure backend has CORS enabled
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  // or specific URLs
)
```

### Blank Page
1. Check browser console for errors
2. Verify `REACT_APP_API_URL` is correct
3. Ensure backend is running

### No Data
1. Check backend is returning data (`/api/metrics/current`)
2. Verify API response in Network tab
3. Check browser console for errors

### Build Errors
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
npm start
```

## 📚 Resources

- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Recharts](https://recharts.org)
- [Lucide Icons](https://lucide.dev)

## 📞 Support

For issues:
1. Check browser console (F12)
2. Check backend logs
3. Test API endpoints with Postman/curl
4. Review error messages in dashboard UI

---

**Dashboard Frontend v1.0.0** | Production Ready
