import { View, Pressable, Text } from "react-native";

type RatingStarsProps = {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
};

export default function RatingStars({ value, onChange, disabled }: RatingStarsProps) {
  return (
    <View className="flex-row gap-4">
      {[1, 2, 3, 4, 5].map((star) => (
        <Pressable
          key={star}
          onPress={() => !disabled && onChange(star)}
          className="opacity-100"
          style={({ pressed }) => ({ opacity: pressed ? 0.6 : 1 })}
        >
          <Text className="text-3xl text-blue-500">{star <= value ? "★" : "☆"}</Text>
        </Pressable>
      ))}
    </View>
  );
}
