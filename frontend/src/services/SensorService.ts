import type { DashboardData, Sensor, SensorHistoryResponse, SensorReading } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const SensorService = {
  getSensors: async (): Promise<Sensor[]> => {
    // Liste statique des 50 capteurs simulés
    const sensors: Sensor[] = Array.from({ length: 50 }, (_, i) => ({
      sensor_id: `sensor_${String(i + 1).padStart(3, '0')}`
    }));
    return Promise.resolve(sensors);
  },

  getSensorById: async (sensorId: string): Promise<Sensor | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/sensors/${sensorId}`);
      if (!response.ok) throw new Error('Failed to fetch sensor details');
      return await response.json();
    } catch (error) {
      console.error('Error fetching sensor details:', error);
      return null;
    }
  },

  getDashboardData: async (sensorId: string, range: 'live' | '1h' | '24h' | '7d' = 'live'): Promise<DashboardData> => {
    try {
      // 1. Fetch History
      let hours = 24;
      if (range === 'live' || range === '1h') hours = 1;
      if (range === '7d') hours = 168;

      const historyResponse = await fetch(`${API_BASE_URL}/sensors/${sensorId}/history?hours=${hours}&limit=50`);
      if (!historyResponse.ok) throw new Error('Failed to fetch history');
      const historyData: SensorHistoryResponse = await historyResponse.json();

      // 2. Fetch Sensor details to get stats (Optimized)
      const sensorInfo = await SensorService.getSensorById(sensorId);

      if (!sensorInfo || !sensorInfo.stats) {
          throw new Error('Sensor stats not found');
      }

      return {
        sensor: { sensor_id: sensorId },
        stats: sensorInfo.stats,
        history: historyData.readings.map((r: SensorReading) => ({
          timestamp: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          value: r.value
        })).reverse()
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }
};
