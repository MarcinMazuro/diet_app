import { Text, View } from "react-native";
export default function Index() {
  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "darkblue",
      }}
    >
      <Text
      style={{ color: "orange", fontSize: 24, marginBottom: 20 }}
      >Main view (Adding products)</Text>
     
    </View>
  );
}
