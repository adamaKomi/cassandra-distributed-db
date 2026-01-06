import React, { useState, useEffect } from 'react';
import StatCard from './StatCard';
import ChartSection from './ChartSection';
import { SensorService } from '../../services/SensorService';
import type { DashboardData, Sensor } from '../../types';

const Dashboard: React.FC = () => {
  const [selectedSensorId, setSelectedSensorId] = useState('');
  const [selectedRange, setSelectedRange] = useState<'live' | '1h' | '24h' | '7d'>('live');
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load available sensors on mount
  useEffect(() => {
    SensorService.getSensors()
      .then(list => {
        setSensors(list);
        if (list.length > 0 && !selectedSensorId) {
            setSelectedSensorId(list[0].sensor_id);
        }
      })
      .catch(err => {
        console.error('Failed to load sensors:', err);
        setError('Impossible de récupérer la liste des capteurs. Vérifiez que l\'API est lancée.');
        setLoading(false);
      });
  }, []);

  // Load dashboard data when sensor or range changes
  useEffect(() => {
    if (!selectedSensorId) return;
    setLoading(true);
    setError(null);
    SensorService.getDashboardData(selectedSensorId, selectedRange)
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Dashboard data error:', err);
        setError('Données indisponibles pour ce capteur.');
        setLoading(false);
      });
  }, [selectedSensorId, selectedRange]);

  if (error && !data) {
    return (
      <div className="flex flex-col h-64 items-center justify-center text-center p-8">
        <span className="material-symbols-outlined text-red-500 text-5xl mb-4">error</span>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Erreur de connexion</h3>
        <p className="text-slate-500 max-w-sm">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-6 px-6 py-2 bg-primary text-white rounded-xl font-semibold hover:bg-primary/90 transition-colors"
        >
          Réessayer
        </button>
      </div>
    );
  }

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
                <option key={sensor.sensor_id} value={sensor.sensor_id}>
                  {sensor.sensor_id}
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
          value={`${data.stats.current_value}°C`} 
          icon="thermostat" 
          trend={`${data.stats.trend_percentage > 0 ? '+' : ''}${data.stats.trend_percentage}%`} 
          trendLabel={data.stats.trend_label}
          color="primary"
        />
        <StatCard 
          title="Avg Value" 
          value={`${data.stats.average_value}°C`} 
          subValueLabel="Daily Average"
          icon="bolt" 
        />
      </div>

      <ChartSection 
        data={data.history} 
        currentValue={data.stats.current_value} 
        selectedRange={selectedRange}
        onRangeChange={setSelectedRange}
      />
    </div>
  );
};

export default Dashboard;
