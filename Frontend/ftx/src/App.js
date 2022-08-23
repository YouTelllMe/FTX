// Library imports.
import { React } from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";

// Component imports.
import Rates from "./pages/Rates.js";
import Profile from "./pages/Profile.js";
import Order from "./pages/Order.js";
import Settings from "./pages/Settings.js";

// Style imports.

// Media imports.

export default function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<Navigate replace to="/rates" />} />
        <Route path="/rates" element={<Rates />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/order" element={<Order />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/*" element={<Rates />} />
      </Routes>
    </Router>
  );
}
