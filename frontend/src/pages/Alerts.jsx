import React, { useEffect, useState } from 'react';
import api from '../api';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    api.get('/api/alerts').then(res => setAlerts(res.data));
  }, []);

  return (
    <div>
      <h2>Live Threat Alerts</h2>
      <ul>
        {alerts.map((alert, idx) => (
          <li key={idx}>
            ⚠️ {alert.type} — {alert.details}
          </li>
        ))}
      </ul>
    </div>
  );
}
