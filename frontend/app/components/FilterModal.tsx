import React, { useState } from "react";
import { View, Text, Modal, Button, TextInput, StyleSheet } from "react-native";
import RNPickerSelect from "react-native-picker-select";

type Props = {
  visible: boolean;
  onApply: (category?: string, min?: number, max?: number) => void;
  onReset: () => void;
  selectedCategory?: string;
  minCalories?: number;
  maxCalories?: number;
};


export default function FilterModal({
  visible,
  onApply,
  onReset,
  selectedCategory,
  minCalories,
  maxCalories,
  
}: Props) {
  const [category, setCategory] = useState(selectedCategory);
  const [minCal, setMinCal] = useState(minCalories?.toString() || "");
  const [maxCal, setMaxCal] = useState(maxCalories?.toString() || "");

React.useEffect(() => {
    setCategory(selectedCategory);
    setMinCal(minCalories?.toString() || "");
    setMaxCal(maxCalories?.toString() || "");
  }, [visible, selectedCategory, minCalories, maxCalories]);  

  return (
    <Modal visible={visible} animationType="slide">
      <View style={styles.container}>
        <Text style={styles.title}>Filters</Text>

        <RNPickerSelect
          onValueChange={setCategory}
          value={category}
          items={[
            { label: "Dinner", value: "dinner" },
            { label: "Lunch", value: "lunch" },
            { label: "Breakfast", value: "breakfast" },
          ]}
          placeholder={{ label: "Select category...", value: undefined }}
          style={{ inputAndroid: styles.picker, inputIOS: styles.picker }}
        />

        <TextInput
          placeholder="Min Calories"
          keyboardType="numeric"
          value={minCal}
          onChangeText={setMinCal}
          style={styles.input}
        />
        <TextInput
          placeholder="Max Calories"
          keyboardType="numeric"
          value={maxCal}
          onChangeText={setMaxCal}
          style={styles.input}
        />
        

        <View style={styles.buttons}>
          <Button
            title="Apply"
            onPress={() =>
              onApply(category, minCal ? parseInt(minCal) : undefined, maxCal ? parseInt(maxCal) : undefined)
            }
          />
          <Button title="Reset" color="red" onPress={onReset} />
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, justifyContent: "center" },
  title: { fontSize: 18, fontWeight: "bold", marginBottom: 12 },
  input: { borderWidth: 1, borderRadius: 6, padding: 8, marginVertical: 6 },
  picker: { borderWidth: 1, borderRadius: 6, padding: 8, marginVertical: 6 },
  buttons: { flexDirection: "row", justifyContent: "space-around", marginTop: 16 },
});
