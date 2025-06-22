// src/App.tsx

import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './services/AuthContext';
import Navbar from './components/layout/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import { Toaster } from "@/components/ui/sonner"


// Import our page components
import LoginPage from './features/auth/LoginPage';
import RegisterPage from './features/auth/RegisterPage';
import DashboardPage from './features/dashboard/DashboardPage';
import DeviceDetailsPage from './features/dashboard/DeviceDetailsPage'; // <-- Add import
import ConversationPage from './features/conversation/ConversationPage';


function App() {
  return (
    // The AuthProvider makes authentication state (like 'isAuthenticated')
    // available to all components, including the Navbar.
    <AuthProvider>
      {/* The Navbar will be displayed on every page */}
      <Navbar />

      {/* The <main> element will hold the content for each specific page */}
      <main className="container mx-auto p-4">
        <Routes>
          {/* Define the route for each page */}
          <Route path="/" element={<DashboardPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/device/:deviceId" element={<DeviceDetailsPage />} />
          <Route 
            path="/conversation" 
            element={
              <ProtectedRoute>
                <ConversationPage />
              </ProtectedRoute>
            } 
          />
          {/* You can add more routes here later, like for a specific device page */}
          {/* e.g., <Route path="/device/:id" element={<DeviceDetailsPage />} /> */}
        </Routes>
      </main>
      <Toaster />
    </AuthProvider>
  );
}

export default App;