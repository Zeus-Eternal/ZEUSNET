// src/pages/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import SignalChart from '../components/SignalChart';
import api from '../api';

export default function Dashboard() {
  const [networks, setNetworks] = useState([]);
  const [tab, setTab] = useState('live');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/api/networks?limit=50');
        console.log('Fetched networks:', res.data);
        setNetworks(res.data);
      } catch (err) {
        console.error('Error fetching networks:', err);
      }
    };

    fetchData();
  }, []);

  const filtered = networks.filter(n => n.rssi >= -85); // example filter

  return (
    <div style={{ padding: '1rem' }}>
      <h1>ZeusNet Dashboard</h1>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        {['live', 'top', 'map'].map(key => (
          <button
            key={key}
            onClick={() => setTab(key)}
            style={{
              padding: '0.5rem 1rem',
              background: tab === key ? '#333' : '#eee',
              color: tab === key ? '#fff' : '#000',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            {key.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Conditional tab content */}
      {tab === 'live' && <SignalChart data={filtered} />}
      {tab === 'top' && <ul>
        {networks
          .sort((a, b) => b.rssi - a.rssi)
          .slice(0, 10)
          .map((n, i) => (
            <li key={i}>{n.ssid} - {n.rssi} dBm</li>
          ))}
      </ul>}
      {tab === 'map' && <p>[Map View Placeholder]</p>}
    </div>
  );
}
