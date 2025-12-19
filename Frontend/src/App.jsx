import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./index.css";
import Home from "./pages/Home";
import Products from "./pages/product";

function App() {
  return (
    <div className="bg-gray-50 min-h-screen">
      <Router>
        {/* Vous pouvez ajouter un composant Navbar ici si vous en avez un */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;