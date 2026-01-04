export interface SensorDataPoint {
  timestamp: string;
  value: number;
}

export interface SensorStats {
  currentValue: number;
  averageValue: number;
  trendPercentage: number;
  trendLabel: string;
}

export interface Sensor {
  id: string;
  name: string;
  location: string;
}

export interface DashboardData {
  sensor: Sensor;
  stats: SensorStats;
  history: SensorDataPoint[];
}
