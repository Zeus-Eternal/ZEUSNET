import React from 'react';
import { MapContainer, TileLayer, HeatmapLayer } from 'react-leaflet';

export default function MapView() {
  // Mocked example points for now
  const positions = [[42.3, -83.1], [42.31, -83.09]];

  return (
    <div>
      <h2>Signal Heatmap</h2>
      <MapContainer center={[42.3, -83.1]} zoom={13} style={{ height: '500px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <HeatmapLayer points={positions.map(([lat, lng]) => ({ lat, lng, intensity: 1 }))} />
      </MapContainer>
    </div>
  );
}
