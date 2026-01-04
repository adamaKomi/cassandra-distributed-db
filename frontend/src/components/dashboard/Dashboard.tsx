import React, { useState, useEffect } from 'react';
import StatCard from './StatCard';
import ChartSection from './ChartSection';
import { SensorService } from '../../services/SensorService';
import type { DashboardData, Sensor } from '../../types';

const Dashboard: React.FC = () => {
  const [selectedSensorId, setSelectedSensorId] = useState('s1');
  const [selectedRange, setSelectedRange] = useState<'live' | '1h' | '24h' | '7d'>('live');
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  // Load available sensors on mount
  useEffect(() => {
    SensorService.getSensors().then(setSensors);
  }, []);

  // Load dashboard data when sensor or range changes
  useEffect(() => {
    setLoading(true);
    SensorService.getDashboardData(selectedSensorId, selectedRange).then(data => {
      setData(data);
      setLoading(false);
    });
  }, [selectedSensorId, selectedRange]);

  if (!data) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className={`transition-opacity duration-200 ${loading ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Dashboard Overview</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-lg">Real-time telemetry data stream from distributed IoT sensors.</p>
        </div>
        <div className="relative min-w-[320px]">
          <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-2 ml-1 uppercase tracking-wider">Active Sensor Source</label>
          <div className="relative group">
            <select 
              value={selectedSensorId}
              onChange={(e) => setSelectedSensorId(e.target.value)}
              className="appearance-none w-full bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 group-hover:border-primary/50 text-slate-900 dark:text-white text-base font-semibold rounded-xl py-3.5 pl-5 pr-12 focus:outline-none focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all cursor-pointer shadow-soft"
            >
              {sensors.map(sensor => (
                <option key={sensor.id} value={sensor.id}>
                  {sensor.name} ({sensor.location})
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400 group-hover:text-primary transition-colors">
              <span className="material-symbols-outlined">expand_more</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <StatCard 
          title="Current Reading" 
          value={`${data.stats.currentValue}°C`} 
          icon="thermostat" 
          trend={`+${data.stats.trendPercentage}%`} 
          trendLabel={data.stats.trendLabel}
          color="primary"
        />
        <StatCard 
          title="Avg Value" 
          value={`${data.stats.averageValue}°C`} 
          subValueLabel="Daily Average"
          icon="bolt" 
        />
      </div>

      <ChartSection 
        data={data.history} 
        currentValue={data.stats.currentValue} 
        selectedRange={selectedRange}
        onRangeChange={setSelectedRange}
      />
    </div>
  );
};

export default Dashboard;
