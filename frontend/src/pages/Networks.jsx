import React, { useEffect, useState } from 'react';
import api from '../api';

export default function Networks() {
  const [mode, setMode] = useState('SAFE');
  const [networks, setNetworks] = useState([]);
  const [filters, setFilters] = useState({ ssid: '', auth: '', limit: 100 });

  const fetchSettings = async () => {
    const res = await api.get('/api/settings');
    setMode(res.data.mode);
  };

  const fetchNetworks = async () => {
    const params = {};
    if (filters.limit) params.limit = filters.limit;
    if (filters.ssid) params.ssid = filters.ssid;
    if (filters.auth) params.auth = filters.auth;
    const res = await api.get('/api/networks', { params });
    setNetworks(res.data);
  };

  useEffect(() => {
    fetchSettings();
    fetchNetworks();
  }, []);

  const header = (
    <tr>
      <th>SSID</th>
      {mode === 'AGGRESSIVE' && <th>BSSID</th>}
      <th>RSSI</th>
      {mode === 'AGGRESSIVE' && <th>Channel</th>}
      {mode === 'AGGRESSIVE' && <th>Auth</th>}
      {mode === 'AGGRESSIVE' && <th>Time</th>}
    </tr>
  );

  const rows = networks.map(n => (
    <tr key={n.id}>
      <td>{n.ssid}</td>
      {mode === 'AGGRESSIVE' && <td>{n.bssid}</td>}
      <td>{n.rssi}</td>
      {mode === 'AGGRESSIVE' && <td>{n.channel}</td>}
      {mode === 'AGGRESSIVE' && <td>{n.auth}</td>}
      {mode === 'AGGRESSIVE' && (
        <td>{String(n.timestamp).replace('T', ' ').split('.')[0]}</td>
      )}
    </tr>
  ));

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Networks</h2>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          placeholder="SSID"
          value={filters.ssid}
          onChange={e => setFilters({ ...filters, ssid: e.target.value })}
        />
        <input
          placeholder="Auth"
          value={filters.auth}
          onChange={e => setFilters({ ...filters, auth: e.target.value })}
        />
        <input
          type="number"
          placeholder="Limit"
          value={filters.limit}
          onChange={e => setFilters({ ...filters, limit: Number(e.target.value) })}
        />
        <button onClick={fetchNetworks}>Apply</button>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead style={{ background: '#f0f0f0' }}>{header}</thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  );
}
