export interface SensorDataPoint {
  timestamp: string;
  value: number;
}

export interface SensorStats {
  current_value: number;
  average_value: number;
  trend_percentage: number;
  trend_label: string;
}

export interface Sensor {
  sensor_id: string;
  last_reading?: SensorReading;
  stats?: SensorStats;
  total_readings?: number;
}

export type SensorInfo = Sensor;

export interface SensorReading {
  sensor_id: string;
  timestamp: string;
  value: number;
}

export interface SensorHistoryResponse {
  sensor_id: string;
  readings: SensorReading[];
  count: number;
}

export interface DashboardData {
  sensor: Sensor;
  stats: SensorStats;
  history: SensorDataPoint[];
}
