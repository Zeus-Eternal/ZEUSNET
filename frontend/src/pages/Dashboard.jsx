import React, { useEffect, useState } from 'react';
import api from '../api';
import SignalChart from '../components/SignalChart';

export default function Dashboard() {
  const [networks, setNetworks] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const res = await api.get('/networks?limit=50');
      setNetworks(res.data);
    };
    fetchData();
  }, []);

  return (
    <div>
      <h2>Live SSID / RSSI Dashboard</h2>
      <SignalChart data={networks} />
    </div>
  );
}
