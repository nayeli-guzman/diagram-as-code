import { Routes, Route } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import Login from "./components/Login";
import Signup from "./components/Signup";
import DiagramEditor from "./components/DiagramEditor";
import LandingPage from "./components/LandingPage";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/editor"
        element={
          <ProtectedRoute>
            <DiagramEditor />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
