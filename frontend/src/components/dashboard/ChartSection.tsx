import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import type { SensorDataPoint } from '../../types';

interface ChartSectionProps {
  data: SensorDataPoint[];
  currentValue: number;
  selectedRange: 'live' | '1h' | '24h' | '7d';
  onRangeChange: (range: 'live' | '1h' | '24h' | '7d') => void;
}

const ChartSection: React.FC<ChartSectionProps> = ({ data, currentValue, selectedRange, onRangeChange }) => {
  const ranges: ('live' | '1h' | '24h' | '7d')[] = ['live', '1h', '24h', '7d'];

  return (
    <div className="w-full">
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-card flex flex-col overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-700 flex flex-wrap justify-between items-center gap-4 bg-slate-50/50 dark:bg-slate-800/50">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              Temperature History
              <span className={`flex h-2 w-2 rounded-full ${selectedRange === 'live' ? 'bg-red-500 animate-pulse' : 'bg-slate-300'}`} title="Live Recording"></span>
            </h3>
            <p className="text-sm text-slate-500">
              {selectedRange === 'live' ? 'Live data stream over the last 20 minutes' : `Historical data over the last ${selectedRange}`}
            </p>
          </div>
          <div className="flex bg-slate-100 dark:bg-slate-700/50 p-1 rounded-lg">
            {ranges.map((range) => (
              <button
                key={range}
                onClick={() => onRangeChange(range)}
                className={`px-3 py-1.5 text-xs font-semibold rounded shadow-sm transition-all uppercase ${
                  selectedRange === range
                    ? 'bg-white dark:bg-slate-600 text-slate-900 dark:text-white'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-slate-600/50'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
        
        <div className="relative w-full h-[400px] p-6 bg-white dark:bg-slate-800">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2b8cee" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#2b8cee" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="timestamp" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
                minTickGap={30}
              />
              <YAxis 
                domain={['auto', 'auto']} 
                hide={true} 
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: 'none', 
                  borderRadius: '8px', 
                  color: '#fff',
                  fontSize: '12px'
                }}
                itemStyle={{ color: '#fff' }}
                cursor={{ stroke: '#2b8cee', strokeWidth: 1, strokeDasharray: '4 4' }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#2b8cee" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorValue)" 
                isAnimationActive={true}
              />
            </AreaChart>
          </ResponsiveContainer>

          {/* Floating Current Value Indicator (Mock position for now, ideally calc from last data point) */}
          <div className="absolute top-10 right-10 flex flex-col items-center animate-bounce duration-[2000ms]">
             <div className="bg-slate-800 text-white text-[11px] px-2.5 py-1.5 rounded-lg shadow-xl font-bold border border-slate-700">
                {currentValue}°C
             </div>
             <div className="w-0 h-0 border-l-[4px] border-l-transparent border-r-[4px] border-r-transparent border-t-[4px] border-t-slate-800"></div>
             <div className="w-3 h-3 bg-primary rounded-full mt-1 ring-4 ring-primary/20"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartSection;
