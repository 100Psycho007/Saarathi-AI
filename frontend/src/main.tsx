import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { registerSW } from 'virtual:pwa-register'

// Register service worker for PWA
registerSW({
  onNeedRefresh() {
    // Future: show toast "New version available"
  },
  onOfflineReady() {
    // Future: show "Ready to work offline" message
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
