import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function SignalChart({ data }) {
  const colorFor = (rssi) => {
    if (rssi > -60) return 'green';
    if (rssi > -75) return 'orange';
    return 'red';
  };

  return (
    <LineChart width={800} height={400} data={data}>
      <XAxis dataKey="ssid" />
      <YAxis domain={[-100, 0]} />
      <Tooltip />
      <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
      <Line
        type="monotone"
        dataKey="rssi"
        stroke="#8884d8"
        dot={({ payload }) => ({
          r: 5,
          stroke: colorFor(payload.rssi),
          strokeWidth: 2,
          fill: colorFor(payload.rssi),
        })}
      />
    </LineChart>
  );
}
