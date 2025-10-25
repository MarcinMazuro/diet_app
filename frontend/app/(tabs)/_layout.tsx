import MaterialCommunityIcons from '@expo/vector-icons/MaterialCommunityIcons';
import { Tabs } from "expo-router";
export default function TabsLayout() {
  return  (

  <Tabs screenOptions={{ tabBarActiveTintColor: "coral" }} >
    <Tabs.Screen 
        name="index" 
      options={{title: "Home Screen", 
        tabBarIcon: ({ color, size }) => (
          <MaterialCommunityIcons name="food-apple" size={24} color={color} />
          ),
        }}
    />

    <Tabs.Screen 
      name="test" 
      options={{title: "Test Screen"
        }}
    />

  </Tabs>
 );
}
