import React, { useState } from 'react';
import TaskStatistics from './TaskStatistics';
import ProductivityMetrics from './ProductivityMetrics';

interface StatisticsPanelProps {
  refreshTrigger?: number;
}

const StatisticsPanel: React.FC<StatisticsPanelProps> = ({ refreshTrigger }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'productivity'>('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Show refresh indicator briefly when data updates
  React.useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      setIsRefreshing(true);
      const timer = setTimeout(() => setIsRefreshing(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [refreshTrigger]);

  const tabs = [
    {
      id: 'overview' as const,
      label: 'Task Overview',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      description: 'Current task status and completion rates'
    },
    {
      id: 'productivity' as const,
      label: 'Productivity',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      description: 'Performance metrics and insights'
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'text-violet-600 border-b-2 border-violet-600 bg-violet-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </div>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Description */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
        <p className="text-xs text-gray-600 text-center">
          {tabs.find(tab => tab.id === activeTab)?.description}
        </p>
      </div>

      {/* Tab Content */}
      <div className="p-0">
        {activeTab === 'overview' && (
          <div className="p-4">
            <TaskStatistics refreshTrigger={refreshTrigger} />
          </div>
        )}
        
        {activeTab === 'productivity' && (
          <div className="p-4">
            <ProductivityMetrics refreshTrigger={refreshTrigger} />
          </div>
        )}
      </div>

      {/* Quick Stats Footer */}
      <div className="bg-gray-50 px-4 py-2 border-t border-gray-100">
        <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full transition-all duration-300 ${isRefreshing ? 'bg-violet-500 animate-pulse' : 'bg-violet-400'}`}></div>
            <span>Real-time updates</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Auto-refresh enabled</span>
          </div>
          {isRefreshing && (
            <div className="flex items-center gap-1 text-violet-600">
              <div className="w-3 h-3 border border-violet-300 border-t-violet-600 rounded-full animate-spin"></div>
              <span>Updating...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatisticsPanel;