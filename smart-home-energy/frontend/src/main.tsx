// src/main.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'; // <-- 1. Ensure this is imported
import App from './App'; // Assuming App is in App.tsx now
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter> {/* <-- 2. This wrapper MUST be here, around <App /> */}
      <App />
    </BrowserRouter>
  </React.StrictMode>
);