import React from 'react';
import { MapContainer, TileLayer, CircleMarker } from 'react-leaflet';

export default function MapView() {
  // Mocked example points for now
  const positions = [[42.3, -83.1], [42.31, -83.09]];

  return (
    <div>
      <h2>Signal Heatmap</h2>
      <MapContainer center={[42.3, -83.1]} zoom={13} style={{ height: '500px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {positions.map(([lat, lng], idx) => (
          <CircleMarker
            key={idx}
            center={[lat, lng]}
            radius={10}
            pathOptions={{ color: 'red' }}
          />
        ))}
      </MapContainer>
    </div>
  );
}
