import React from 'react';
import api from '../api';

export default function ControlPanel() {
  const sendCommand = (opcode, payload = {}) => {
    api.post('/api/command', { opcode, payload });
  };

  return (
    <div>
      <h3>ESP32 Command Panel</h3>
      <button onClick={() => sendCommand(0x01, { interval: 5 })}>Set Scan Interval</button>
      <button onClick={() => sendCommand(0x20)}>Reboot ESP32</button>
    </div>
  );
}
