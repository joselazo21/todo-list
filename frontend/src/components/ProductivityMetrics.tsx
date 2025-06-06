import React, { useEffect, useState } from 'react';
import todoService from '../services/todoService';
import type { IProductivityMetrics } from "../types/types.ts";

interface ProductivityMetricsProps {
  refreshTrigger?: number;
}

const ProductivityMetrics: React.FC<ProductivityMetricsProps> = ({ refreshTrigger }) => {
  const [metrics, setMetrics] = useState<IProductivityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDays, setSelectedDays] = useState(30);

  const fetchMetrics = async () => {
    try {
      // Only show loading on initial load or when changing days, not on refreshes
      if (!metrics || selectedDays !== selectedDays) {
        setLoading(true);
      }
      const data = await todoService.getProductivityMetrics(selectedDays);
      setMetrics(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching productivity metrics:', err);
      setError('Failed to load productivity metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [refreshTrigger, selectedDays]);

  if (loading && !metrics) {
    return (
      <div className="flex justify-center items-center p-4">
        <div className="w-6 h-6 border-t-2 border-violet-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="p-4 bg-red-50 text-red-600 text-sm rounded">
        {error || 'Failed to load productivity metrics'}
      </div>
    );
  }

  const getProductivityColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-blue-600 bg-blue-100';
    if (score >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getProductivityLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Average';
    return 'Needs Improvement';
  };

  const formatTime = (hours: number) => {
    if (hours < 1) {
      return `${Math.round(hours * 60)}m`;
    } else if (hours < 24) {
      return `${hours.toFixed(1)}h`;
    } else {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return `${days}d ${remainingHours.toFixed(1)}h`;
    }
  };

  return (
    <div className="transition-all duration-300 ease-in-out">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-medium text-gray-800">Productivity Metrics</h2>
        <div className="flex items-center gap-2">
          {loading && metrics && (
            <div className="w-4 h-4 border border-violet-300 border-t-violet-600 rounded-full animate-spin"></div>
          )}
          <select
            className="border border-gray-200 rounded-md p-1 text-sm bg-white transition-all duration-200 hover:border-violet-300 focus:border-violet-500 focus:outline-none"
            value={selectedDays}
            onChange={(e) => setSelectedDays(Number(e.target.value))}
            disabled={loading}
          >
            <option value={7}>Last 7 days</option>
            <option value={15}>Last 15 days</option>
            <option value={30}>Last 30 days</option>
            <option value={60}>Last 60 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Productivity Score - Main Metric */}
      <div className="mb-6">
        <div className="text-center">
          <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${getProductivityColor(metrics.productivity_score)} mb-2 transition-all duration-500 transform hover:scale-105`}>
            <span className="text-2xl font-bold transition-all duration-500">{Math.round(metrics.productivity_score)}</span>
          </div>
          <div className="text-sm font-medium text-gray-700">
            Productivity Score
          </div>
          <div className={`text-xs px-2 py-1 rounded-full inline-block mt-1 transition-all duration-300 ${getProductivityColor(metrics.productivity_score)}`}>
            {getProductivityLabel(metrics.productivity_score)}
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-blue-50 p-3 rounded-lg text-center transition-all duration-300 hover:shadow-md hover:bg-blue-100">
          <div className="text-2xl font-bold text-blue-700 transition-all duration-500">{metrics.total_tasks}</div>
          <div className="text-sm text-blue-600">Total Tasks</div>
          <div className="text-xs text-blue-500 mt-1">Last {selectedDays} days</div>
        </div>

        <div className="bg-green-50 p-3 rounded-lg text-center transition-all duration-300 hover:shadow-md hover:bg-green-100">
          <div className="text-2xl font-bold text-green-700 transition-all duration-500">{metrics.completed_tasks}</div>
          <div className="text-sm text-green-600">Completed</div>
          <div className="text-xs text-green-500 mt-1 transition-all duration-500">
            {Math.round(metrics.completion_rate)}% completion rate
          </div>
        </div>
      </div>

      {/* Completion Rate Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Completion Rate</span>
          <span className="transition-all duration-500">{Math.round(metrics.completion_rate)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-700 ease-out"
            style={{ width: `${Math.min(100, metrics.completion_rate)}%` }}
          ></div>
        </div>
      </div>

      {/* Average Completion Time */}
      <div className="bg-purple-50 p-3 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-purple-700">Average Completion Time</div>
            <div className="text-xs text-purple-600">Time from creation to completion</div>
          </div>
          <div className="text-right">
            <div className="text-xl font-bold text-purple-700">
              {formatTime(metrics.average_completion_time)}
            </div>
            <div className="text-xs text-purple-600">per task</div>
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="border-t border-gray-100 pt-3 mt-3">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Insights</h3>
        <div className="space-y-2 text-xs text-gray-600">
          {metrics.completion_rate >= 80 && (
            <div className="flex items-center text-green-600">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Great job! You're completing most of your tasks.
            </div>
          )}
          {metrics.completion_rate < 50 && (
            <div className="flex items-center text-yellow-600">
              <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
              Consider breaking down large tasks into smaller ones.
            </div>
          )}
          {metrics.average_completion_time > 72 && (
            <div className="flex items-center text-blue-600">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
              Tasks are taking a while to complete. Try setting shorter deadlines.
            </div>
          )}
          {metrics.productivity_score >= 80 && (
            <div className="flex items-center text-green-600">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Excellent productivity! Keep up the great work.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductivityMetrics;