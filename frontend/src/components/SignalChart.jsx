<Line
  type="monotone"
  dataKey="rssi"
  stroke="#8884d8"
  strokeWidth={2}
  dot={({ payload }) => {
    const strength = payload.rssi;
    let color = '#ccc';
    if (strength > -60) color = 'green';
    else if (strength > -75) color = 'orange';
    else color = 'red';
    return {
      r: 5,
      stroke: color,
      strokeWidth: 2,
      fill: color,
    };
  }}
/>
