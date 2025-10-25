import { Text, View } from 'react-native';
import React, { useState, useEffect } from 'react';
import Constants from 'expo-constants';



const apiUrl = process.env.EXPO_PUBLIC_API_URL;


export default function Test() {
  const [data, setData] = useState('Ładowanie...'); 

 useEffect(() => {
    fetch(apiUrl!)
      .then(response => response.json())
      .then(jsonData => setData(jsonData.message))
      .catch(error => setData(`BŁĄD: ${error.name} - ${error.message}`));
  }, []);

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold' }}>
        {data}
      </Text>
    </View>
  );
}