import React from 'react';
import api from '../api';

export default function ExportButton() {
  const handleExport = async () => {
    const res = await api.get('/api/export/csv', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'wifi_export.csv');
    document.body.appendChild(link);
    link.click();
  };

  return <button onClick={handleExport}>Download CSV</button>;
}
