import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { activityService, Activity } from '../services/activityService';
import { placeService, Place } from '../services/placeService';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const navigation = useNavigation();
  const [featuredActivities, setFeaturedActivities] = useState<Activity[]>([]);
  const [featuredPlaces, setFeaturedPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [activities, places] = await Promise.all([
        activityService.getActivities({ sort: 'featured' }),
        placeService.getPlaces({ sort: 'featured' }),
      ]);
      setFeaturedActivities(activities.slice(0, 5));
      setFeaturedPlaces(places.slice(0, 5));
    } catch (error) {
      console.error('Error loading home data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderActivityCard = (activity: Activity) => (
    <TouchableOpacity
      key={activity.id}
      style={styles.card}
      onPress={() => navigation.navigate('ActivityDetail' as never, { id: activity.id } as never)}
    >
      {activity.main_image_url && (
        <Image source={{ uri: activity.main_image_url }} style={styles.cardImage} />
      )}
      <View style={styles.cardContent}>
        <Text style={styles.cardTitle} numberOfLines={1}>
          {activity.title}
        </Text>
        <Text style={styles.cardSubtitle} numberOfLines={2}>
          {activity.short_description}
        </Text>
        <View style={styles.cardFooter}>
          <View style={styles.cardMeta}>
            <Ionicons name="calendar-outline" size={14} color="#666" />
            <Text style={styles.cardMetaText}>
              {new Date(activity.start_date).toLocaleDateString()}
            </Text>
          </View>
          <View style={styles.cardMeta}>
            <Ionicons name="people-outline" size={14} color="#666" />
            <Text style={styles.cardMetaText}>
              {activity.participants_count}/{activity.max_participants}
            </Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderPlaceCard = (place: Place) => (
    <TouchableOpacity
      key={place.id}
      style={styles.card}
      onPress={() => navigation.navigate('PlaceDetail' as never, { id: place.id } as never)}
    >
      {place.main_image_url && (
        <Image source={{ uri: place.main_image_url }} style={styles.cardImage} />
      )}
      <View style={styles.cardContent}>
        <View style={styles.placeHeader}>
          <Text style={styles.cardTitle} numberOfLines={1}>
            {place.name}
          </Text>
          {place.is_verified && (
            <Ionicons name="checkmark-circle" size={20} color="#FF5A5F" />
          )}
        </View>
        <Text style={styles.cardSubtitle} numberOfLines={2}>
          {place.short_description}
        </Text>
        <View style={styles.cardFooter}>
          <View style={styles.ratingContainer}>
            <Ionicons name="star" size={14} color="#FFB800" />
            <Text style={styles.ratingText}>{place.rating}</Text>
            <Text style={styles.reviewCount}>({place.review_count})</Text>
          </View>
          <Text style={styles.priceText}>{place.price_display}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome to</Text>
            <Text style={styles.title}>Acteezer</Text>
          </View>
          <TouchableOpacity>
            <Ionicons name="notifications-outline" size={24} color="#000" />
          </TouchableOpacity>
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.quickAction}
            onPress={() => navigation.navigate('Activities' as never)}
          >
            <View style={[styles.quickActionIcon, { backgroundColor: '#FF5A5F' }]}>
              <Ionicons name="calendar" size={24} color="#FFF" />
            </View>
            <Text style={styles.quickActionText}>Activities</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.quickAction}
            onPress={() => navigation.navigate('Places' as never)}
          >
            <View style={[styles.quickActionIcon, { backgroundColor: '#00A699' }]}>
              <Ionicons name="location" size={24} color="#FFF" />
            </View>
            <Text style={styles.quickActionText}>Places</Text>
          </TouchableOpacity>
        </View>

        {/* Featured Activities */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Featured Activities</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Activities' as never)}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalScroll}>
            {featuredActivities.map(renderActivityCard)}
          </ScrollView>
        </View>

        {/* Featured Places */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Featured Places</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Places' as never)}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalScroll}>
            {featuredPlaces.map(renderPlaceCard)}
          </ScrollView>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  greeting: {
    fontSize: 16,
    color: '#666',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#000',
    marginTop: 4,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  quickAction: {
    alignItems: 'center',
  },
  quickActionIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickActionText: {
    fontSize: 14,
    color: '#000',
    fontWeight: '500',
  },
  section: {
    marginTop: 20,
    paddingBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#000',
  },
  seeAll: {
    fontSize: 16,
    color: '#FF5A5F',
    fontWeight: '600',
  },
  horizontalScroll: {
    paddingLeft: 20,
  },
  card: {
    width: width * 0.75,
    backgroundColor: '#FFF',
    borderRadius: 12,
    marginRight: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
    overflow: 'hidden',
  },
  cardImage: {
    width: '100%',
    height: 180,
    resizeMode: 'cover',
  },
  cardContent: {
    padding: 15,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 5,
  },
  placeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 10,
  },
  cardMetaText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#000',
    marginLeft: 4,
  },
  reviewCount: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  priceText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF5A5F',
  },
});

