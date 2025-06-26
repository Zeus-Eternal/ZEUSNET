import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Devices from './pages/Devices';
import Alerts from './pages/Alerts';
import MapView from './pages/MapView';
import Pentest from './pages/Pentest';
import NavBar from './components/NavBar';

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/devices" element={<Devices />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/map" element={<MapView />} />
        <Route path="/pentest" element={<Pentest />} />
      </Routes>
    </BrowserRouter>
  );
}
