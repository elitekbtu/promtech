/**
 * Example Component: Water Objects List with Role-Based Access
 * 
 * This example demonstrates:
 * - Using authentication hooks
 * - Making authenticated API calls
 * - Role-based conditional rendering
 * - Error handling
 */

import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert, StyleSheet } from 'react-native';
import { useState, useEffect } from 'react';
import { useUserRole } from '@/hooks/use-auth';
import { WaterObjectsAPI, WaterObject } from '@/lib/api-services';
import { getErrorMessage } from '@/lib/axios-client';

export default function WaterObjectsScreen() {
  const { role, isExpert, loading: roleLoading } = useUserRole();
  const [objects, setObjects] = useState<WaterObject[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Load water objects on mount
  useEffect(() => {
    loadObjects();
  }, []);

  async function loadObjects() {
    try {
      setLoading(true);
      const response = await WaterObjectsAPI.getList({
        limit: 50,
        sort_by: 'name',
        sort_order: 'asc',
      });
      setObjects(response.items);
    } catch (error) {
      console.error('Failed to load objects:', error);
      Alert.alert('Error', getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    await loadObjects();
    setRefreshing(false);
  }

  async function handleCreateObject() {
    try {
      const newObject = await WaterObjectsAPI.create({
        name: 'New Reservoir',
        region: 'Almaty',
        resource_type: 'reservoir',
        technical_condition: 4,
      });
      
      // Add to list
      setObjects([newObject, ...objects]);
      Alert.alert('Success', 'Water object created!');
    } catch (error) {
      Alert.alert('Error', getErrorMessage(error));
    }
  }

  async function handleDeleteObject(id: number) {
    Alert.alert(
      'Confirm Delete',
      'Are you sure you want to delete this object?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await WaterObjectsAPI.delete(id);
              setObjects(objects.filter(obj => obj.id !== id));
              Alert.alert('Success', 'Object deleted');
            } catch (error) {
              Alert.alert('Error', getErrorMessage(error));
            }
          },
        },
      ]
    );
  }

  function renderItem({ item }: { item: WaterObject }) {
    return (
      <View style={styles.item}>
        <View style={styles.itemHeader}>
          <Text style={styles.itemName}>{item.name}</Text>
          {/* Expert users see priority badge */}
          {isExpert && item.priority_level && (
            <View style={[
              styles.priorityBadge,
              item.priority_level === 'high' && styles.priorityHigh,
              item.priority_level === 'medium' && styles.priorityMedium,
              item.priority_level === 'low' && styles.priorityLow,
            ]}>
              <Text style={styles.priorityText}>{item.priority_level}</Text>
            </View>
          )}
        </View>

        <Text style={styles.itemDetail}>Region: {item.region}</Text>
        <Text style={styles.itemDetail}>Type: {item.resource_type}</Text>
        <Text style={styles.itemDetail}>Condition: {item.technical_condition}/5</Text>

        {/* Expert users see priority score */}
        {isExpert && item.priority_score !== undefined && (
          <Text style={styles.itemDetail}>
            Priority Score: {item.priority_score}
          </Text>
        )}

        {/* Expert users can delete */}
        {isExpert && (
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={() => handleDeleteObject(item.id)}
          >
            <Text style={styles.deleteButtonText}>Delete</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  if (roleLoading || loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Role indicator */}
      <View style={styles.header}>
        <Text style={styles.title}>Water Objects</Text>
        <Text style={styles.roleText}>
          Role: {role === 'expert' ? '👨‍🔬 Expert' : '👤 Guest'}
        </Text>
      </View>

      {/* Guest users see info message */}
      {!isExpert && (
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            ℹ️ You're viewing as Guest. Priority information is hidden.
          </Text>
        </View>
      )}

      {/* Expert users can create objects */}
      {isExpert && (
        <TouchableOpacity
          style={styles.createButton}
          onPress={handleCreateObject}
        >
          <Text style={styles.createButtonText}>+ Create Object</Text>
        </TouchableOpacity>
      )}

      <FlatList
        data={objects}
        renderItem={renderItem}
        keyExtractor={(item) => item.id.toString()}
        refreshing={refreshing}
        onRefresh={handleRefresh}
        ListEmptyComponent={
          <View style={styles.center}>
            <Text>No water objects found</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  roleText: {
    fontSize: 14,
    color: '#666',
  },
  infoBox: {
    backgroundColor: '#e3f2fd',
    padding: 12,
    margin: 16,
    borderRadius: 8,
  },
  infoText: {
    color: '#1976d2',
  },
  createButton: {
    backgroundColor: '#4caf50',
    padding: 16,
    margin: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  item: {
    backgroundColor: '#fff',
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  itemName: {
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityHigh: {
    backgroundColor: '#f44336',
  },
  priorityMedium: {
    backgroundColor: '#ff9800',
  },
  priorityLow: {
    backgroundColor: '#4caf50',
  },
  priorityText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  itemDetail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  deleteButton: {
    backgroundColor: '#f44336',
    padding: 8,
    borderRadius: 4,
    marginTop: 8,
    alignItems: 'center',
  },
  deleteButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
});
