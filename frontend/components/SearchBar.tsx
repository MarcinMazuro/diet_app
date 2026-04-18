import { useState } from "react";
import { View, TextInput, Pressable, Text } from "react-native";

interface SearchBarProps {
  onSearch: (query: string) => void;
  initialValue?: string;
}

export default function SearchBar({ onSearch, initialValue = "" }: SearchBarProps) {
  const [value, setValue] = useState(initialValue);

  return (
    <View className="mb-4 flex-row items-center gap-4">
      <TextInput
        placeholder="Search..."
        value={value}
        onChangeText={setValue}
        className="flex-1 rounded-[28px] border border-blue-300 bg-white px-5 py-4 text-blue-900 text-base"
        returnKeyType="search"
        onSubmitEditing={() => onSearch(value)}
      />
      <Pressable
        className="rounded-[28px] bg-blue-600 px-6 py-4"
        onPress={() => onSearch(value)}
      >
        <Text className="text-base font-semibold text-white">Search</Text>
      </Pressable>
    </View>
  );
}
