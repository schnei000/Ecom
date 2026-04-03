import { BrowserRouter as Router } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import "./index.css";
import AuthProvider from "./context/AuthProvider";
import CartProvider from "./context/cart/CartProvider";
import ThemeProvider from "./context/ThemeProvider";
import AppRoutes from "./routes/AppRoutes";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <CartProvider>
          <Router>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 3000,
                style: {
                  background: 'var(--bg-elevated)',
                  color: 'var(--text)',
                  border: '1px solid var(--border-mid)',
                  boxShadow: 'var(--shadow-md)',
                  backdropFilter: 'blur(18px)',
                  borderRadius: '1rem',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#10b981',
                    secondary: 'var(--bg-card)',
                  },
                },
                error: {
                  duration: 4000,
                  iconTheme: {
                    primary: '#f43f5e',
                    secondary: 'var(--bg-card)',
                  },
                },
              }}
            />
            <AppRoutes />
          </Router>
        </CartProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
