
import { View, Text, Modal, TextInput, Pressable } from "react-native";
import { useState, useEffect } from "react";
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

  useEffect(() => {
    setCategory(selectedCategory);
    setMinCal(minCalories?.toString() || "");
    setMaxCal(maxCalories?.toString() || "");
  }, [visible, selectedCategory, minCalories, maxCalories]);

  return (
    <Modal visible={visible} animationType="slide">
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 p-6 justify-center">
        <View className="rounded-[36px] bg-white border border-blue-200 p-8 shadow-lg">
          <Text className="text-2xl font-semibold text-blue-900 mb-6">Filters</Text>

          <RNPickerSelect
            onValueChange={setCategory}
            value={category}
            items={[
              { label: "Dinner", value: "dinner" },
              { label: "Lunch", value: "lunch" },
              { label: "Breakfast", value: "breakfast" },
            ]}
            placeholder={{ label: "Select category...", value: undefined }}
            style={{
              inputAndroid: {
                backgroundColor: "#eff6ff",
                borderRadius: 20,
                paddingHorizontal: 16,
                paddingVertical: 16,
                marginBottom: 16,
                color: "#1e40af",
              },
              inputIOS: {
                backgroundColor: "#eff6ff",
                borderRadius: 20,
                paddingHorizontal: 16,
                paddingVertical: 16,
                marginBottom: 16,
                color: "#1e40af",
              },
            }}
          />

          <TextInput
            placeholder="Min Calories"
            keyboardType="numeric"
            value={minCal}
            onChangeText={setMinCal}
            className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4 mb-4 text-blue-900 text-base"
          />
          <TextInput
            placeholder="Max Calories"
            keyboardType="numeric"
            value={maxCal}
            onChangeText={setMaxCal}
            className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4 mb-6 text-blue-900 text-base"
          />

          <View className="flex-row gap-4">
            <Pressable
              className="flex-1 rounded-[28px] bg-blue-600 py-5 items-center shadow-md"
              onPress={() =>
                onApply(
                  category,
                  minCal ? parseInt(minCal) : undefined,
                  maxCal ? parseInt(maxCal) : undefined
                )
              }
            >
              <Text className="font-semibold text-white text-base">Apply</Text>
            </Pressable>
            <Pressable
              className="flex-1 rounded-[28px] bg-red-500 py-5 items-center shadow-md"
              onPress={onReset}
            >
              <Text className="font-semibold text-white text-base">Reset</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
}
