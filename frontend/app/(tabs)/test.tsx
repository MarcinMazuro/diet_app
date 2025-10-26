import { Text, View } from 'react-native';
import React, { useState, useEffect } from 'react';
import { API_URL, ENDPOINTS } from '../../config/api';

export default function Test() {
  const [data, setData] = useState('Ładowanie...');

  useEffect(() => {
    const url = `${API_URL}${ENDPOINTS.TEST}`;
    fetch(url)
      .then(async response => {
        const ct = response.headers.get('content-type') ?? '';
        const text = await response.text();
        if (!ct.includes('application/json')) throw new Error(`Nieoczekiwana odpowiedź: ${text}`);
        return JSON.parse(text);
      })
      .then(json => setData(json.message ?? JSON.stringify(json)))
      .catch(err => setData(`BŁĄD: ${err.message}`));
  }, []);

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold' }}>{data}</Text>
    </View>
  );
}