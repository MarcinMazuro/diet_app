import React from "react";
import { View, Pressable, Text, StyleSheet } from "react-native";

type RatingStarsProps = {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
};

export default function RatingStars({ value, onChange, disabled }: RatingStarsProps) {
  return (
    <View style={{ flexDirection: "row" }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <Pressable
          key={star}
          onPress={() => !disabled && onChange(star)}
          style={({ pressed }) => [{ opacity: pressed ? 0.6 : 1 }]}
        >
          <Text style={{ fontSize: 24 }}>{star <= value ? "★" : "☆"}</Text>
        </Pressable>
      ))}
    </View>
  );
}


const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    gap: 4,
  },
});
