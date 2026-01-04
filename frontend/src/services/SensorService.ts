import type { DashboardData, Sensor, SensorDataPoint } from '../types';

const SENSORS: Sensor[] = [
  { id: 's1', name: 'Sensor 01', location: 'Manufacturing Unit' },
  { id: 's2', name: 'Sensor 02', location: 'Assembly Line' },
  { id: 's3', name: 'Sensor 03', location: 'Packaging' },
];

const generateHistory = (baseValue: number, count: number, range: 'live' | '1h' | '24h' | '7d'): SensorDataPoint[] => {
  const history: SensorDataPoint[] = [];
  const now = new Date();
  
  for (let i = count; i >= 0; i--) {
    const time = new Date(now);
    let label = '';

    if (range === 'live') {
      time.setMinutes(now.getMinutes() - i);
      label = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (range === '1h') {
      time.setMinutes(now.getMinutes() - i * 3); // Every 3 mins for 1 hour (20 points)
      label = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (range === '24h') {
      time.setHours(now.getHours() - i);
      label = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (range === '7d') {
      time.setDate(now.getDate() - i);
      label = time.toLocaleDateString([], { weekday: 'short' });
    }

    const randomShift = (Math.random() - 0.5) * 5; 
    history.push({
      timestamp: label,
      value: parseFloat((baseValue + randomShift).toFixed(1))
    });
  }
  return history;
};

export const SensorService = {
  getSensors: (): Promise<Sensor[]> => {
    return Promise.resolve(SENSORS);
  },

  getDashboardData: (sensorId: string, range: 'live' | '1h' | '24h' | '7d' = 'live'): Promise<DashboardData> => {
    // Simulate API delay
    return new Promise((resolve) => {
      setTimeout(() => {
        let baseTemp = 42.5; 
        if (sensorId === 's2') baseTemp = 35.0;
        if (sensorId === 's3') baseTemp = 28.5;

        const currentVal = baseTemp + (Math.random() - 0.5) * 2;
        const avgVal = baseTemp - 2 + Math.random();

        resolve({
          sensor: SENSORS.find(s => s.id === sensorId) || SENSORS[0],
          stats: {
            currentValue: parseFloat(currentVal.toFixed(1)),
            averageValue: parseFloat(avgVal.toFixed(1)),
            trendPercentage: 1.2,
            trendLabel: 'vs last hour'
          },
          history: generateHistory(baseTemp, 20, range) 
        });
      }, 300);
    });
  }
};
