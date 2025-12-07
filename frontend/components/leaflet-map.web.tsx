import React, { useEffect, useRef } from 'react';
import type { WaterObject } from '@/lib/gidroatlas-types';

// Dynamically import Leaflet only on client side
let L: any = null;
if (typeof window !== 'undefined') {
  L = require('leaflet/dist/leaflet-src');
  
  // Fix default marker icon issue in Leaflet
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  });
}

interface LeafletMapProps {
  waterObjects: WaterObject[];
  onMarkerClick?: (objectId: number) => void;
}

// Technical condition colors
const conditionColors: Record<number, string> = {
  1: '#ef4444', // Red - Critical
  2: '#f97316', // Orange - Poor
  3: '#eab308', // Yellow - Fair
  4: '#22c55e', // Green - Good
  5: '#10b981', // Emerald - Excellent
};

export default function LeafletMap({ waterObjects, onMarkerClick }: LeafletMapProps) {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<any[]>([]);

  useEffect(() => {
    // Inject Leaflet CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    link.crossOrigin = '';
    document.head.appendChild(link);

    return () => {
      document.head.removeChild(link);
    };
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined' || !L || !mapContainerRef.current) return;

    // Initialize map
    if (!mapRef.current) {
      const map = L.map(mapContainerRef.current).setView([48.0196, 66.9237], 6);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;
    }

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add markers for water objects
    if (waterObjects.length > 0 && mapRef.current) {
      const bounds = L.latLngBounds([]);

      waterObjects.forEach(obj => {
        if (obj.latitude && obj.longitude) {
          const color = conditionColors[obj.technical_condition] || '#6b7280';
          
          // Create custom colored icon
          const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
          });

          const marker = L.marker([obj.latitude, obj.longitude], { icon })
            .addTo(mapRef.current!)
            .bindPopup(`
              <div style="font-family: system-ui, -apple-system, sans-serif; min-width: 200px;">
                <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">${obj.name}</h3>
                <p style="margin: 4px 0; font-size: 14px; color: #666;"><strong>Регион:</strong> ${obj.region}</p>
                <p style="margin: 4px 0; font-size: 14px; color: #666;"><strong>Тип:</strong> ${obj.resource_type}</p>
                <p style="margin: 4px 0; font-size: 14px; color: #666;"><strong>Тех. состояние:</strong> ${obj.technical_condition}/5</p>
                <button onclick="window.dispatchEvent(new CustomEvent('marker-click', { detail: ${obj.id} }))" style="margin-top: 8px; padding: 8px 16px; background-color: #2D9A86; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600;">Подробнее →</button>
              </div>
            `);

          markersRef.current.push(marker);
          bounds.extend([obj.latitude, obj.longitude]);
        }
      });

      // Fit map to show all markers
      if (bounds.isValid()) {
        mapRef.current.fitBounds(bounds, { padding: [50, 50] });
      }
    }

    // Cleanup
    return () => {
      markersRef.current.forEach(marker => marker.remove());
      markersRef.current = [];
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []); // Initialize once

  // Update markers when waterObjects change
  useEffect(() => {
    if (!mapRef.current || !L) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add markers for water objects
    if (waterObjects.length > 0) {
      const bounds = L.latLngBounds([]);

      waterObjects.forEach(obj => {
        if (obj.latitude && obj.longitude) {
          const color = conditionColors[obj.technical_condition] || '#6b7280';
          
          // Create custom colored icon
          const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
          });

          const marker = L.marker([obj.latitude, obj.longitude], { icon })
            .addTo(mapRef.current!)
            .bindPopup(`
              <div style="font-family: system-ui, -apple-system, sans-serif; min-width: 200px;">
                <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">${obj.name}</h3>
                <p style="margin: 4px 0; font-size: 14px; color: #666;"><strong>Регион:</strong> ${obj.region}</p>
                <p style="margin: 4px 0; font-size: 14px; color: #666;"><strong>Тип:</strong> ${obj.resource_type}</p>
                <p style="margin: 4px 0; font-size: 14px; color: #666;"><strong>Тех. состояние:</strong> ${obj.technical_condition}/5</p>
                <button onclick="window.dispatchEvent(new CustomEvent('marker-click', { detail: ${obj.id} }))" style="margin-top: 8px; padding: 8px 16px; background-color: #2D9A86; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600;">Подробнее →</button>
              </div>
            `);

          markersRef.current.push(marker);
          bounds.extend([obj.latitude, obj.longitude]);
        }
      });

      // Fit map to show all markers
      if (bounds.isValid()) {
        mapRef.current.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [waterObjects]);
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleMarkerClick = (e: any) => {
      if (onMarkerClick) {
        onMarkerClick(e.detail);
      }
    };

    window.addEventListener('marker-click', handleMarkerClick);
    return () => window.removeEventListener('marker-click', handleMarkerClick);
  }, [onMarkerClick]);

  return (
    <div 
      ref={mapContainerRef}
      style={{ 
        width: '100%', 
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1,
      }} 
    />
  );
}
