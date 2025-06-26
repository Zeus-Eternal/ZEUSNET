import React from 'react';
import { Link } from 'react-router-dom';

export default function NavBar() {
  return (
    <nav style={{ display: 'flex', gap: '1rem', padding: '0.5rem' }}>
      <Link to="/">Dashboard</Link>
      <Link to="/devices">Devices</Link>
      <Link to="/networks">Networks</Link>
      <Link to="/alerts">Alerts</Link>
      <Link to="/map">Map</Link>
      <Link to="/pentest">Pentest</Link>
    </nav>
  );
}

