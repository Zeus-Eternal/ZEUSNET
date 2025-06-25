import React, { useEffect, useState } from 'react';
import api from '../api';

export default function Devices() {
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    api.get('/devices').then(res => setDevices(res.data));
  }, []);

  return (
    <div>
      <h2>MAC Tracker</h2>
      <ul>
        {devices.map((dev, idx) => (
          <li key={idx}>
            {dev.mac} — First Seen: {dev.first_seen}, Last Seen: {dev.last_seen}
          </li>
        ))}
      </ul>
    </div>
  );
}
