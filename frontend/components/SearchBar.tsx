import React, { useState } from "react";
import { View, TextInput, Button, StyleSheet } from "react-native";

// Props for SearchBar component
interface SearchBarProps {
  onSearch: (query: string) => void;
  initialValue?: string;
}

export default function SearchBar({ onSearch, initialValue = "" }: SearchBarProps) {
  const [value, setValue] = useState(initialValue);

  return (
    <View style={styles.container}>
      <TextInput
        placeholder="Search..."
        value={value}
        onChangeText={setValue}
        style={styles.input}
        returnKeyType="search"
        onSubmitEditing={() => onSearch(value)}
      />
      <Button title="Search" onPress={() => onSearch(value)} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flexDirection: "row", gap: 8, marginBottom: 12 },
  input: { flex: 1, borderWidth: 1, borderColor: "#ddd", borderRadius: 6, padding: 8 },
});
