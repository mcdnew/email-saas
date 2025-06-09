// src/main.jsx

import React from 'react'
import ReactDOM from 'react-dom/client'

// 1) Import Bootstrap’s CSS first
import 'bootstrap/dist/css/bootstrap.min.css'

// 2) Then your own index.css (if you have custom styles)
import './index.css'

import App from './App'

// This mounts your React app into the <div id="root"> in index.html
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
