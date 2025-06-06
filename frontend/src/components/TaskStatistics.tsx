import React, { useEffect, useState } from 'react';
import todoService from '../services/todoService';
import type {ITaskStatistics} from "../types/types.ts";

interface TaskStatisticsProps {
  refreshTrigger?: number; // Prop to trigger refresh
}

const TaskStatistics: React.FC<TaskStatisticsProps> = ({ refreshTrigger }) => {
  const [statistics, setStatistics] = useState<ITaskStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = async () => {
    try {
      // Only show loading on initial load, not on refreshes
      if (!statistics) {
        setLoading(true);
      }
      const data = await todoService.getTaskStatistics();
      setStatistics(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, [refreshTrigger]); // Re-fetch when refreshTrigger changes

  if (loading && !statistics) {
    return (
      <div className="flex justify-center items-center p-4">
        <div className="w-6 h-6 border-t-2 border-violet-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !statistics) {
    return (
      <div className="p-4 bg-red-50 text-red-600 text-sm rounded">
        {error || 'Failed to load statistics'}
      </div>
    );
  }

  const completionRate = statistics.total_tasks > 0
    ? Math.round((statistics.completed_tasks / statistics.total_tasks) * 100)
    : 0;

  return (
    <div className="transition-all duration-300 ease-in-out">
      <h2 className="text-lg font-medium text-gray-800 mb-3">Task Overview</h2>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-violet-50 p-3 rounded-lg transition-all duration-300 hover:shadow-md">
          <div className="text-2xl font-bold text-violet-700 transition-all duration-500">{statistics.total_tasks}</div>
          <div className="text-sm text-violet-600">Total Tasks</div>
        </div>

        <div className="bg-green-50 p-3 rounded-lg transition-all duration-300 hover:shadow-md">
          <div className="text-2xl font-bold text-green-700 transition-all duration-500">{statistics.completed_tasks}</div>
          <div className="text-sm text-green-600">Completed</div>
        </div>

        <div className="bg-yellow-50 p-3 rounded-lg transition-all duration-300 hover:shadow-md">
          <div className="text-2xl font-bold text-yellow-700 transition-all duration-500">{statistics.pending_tasks}</div>
          <div className="text-sm text-yellow-600">Pending</div>
        </div>

        <div className="bg-red-50 p-3 rounded-lg transition-all duration-300 hover:shadow-md">
          <div className="text-2xl font-bold text-red-700 transition-all duration-500">{statistics.overdue_tasks}</div>
          <div className="text-sm text-red-600">Overdue</div>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Completion Rate</span>
          <div className="flex items-center gap-2">
            <span className="transition-all duration-500">{completionRate}%</span>
            {loading && statistics && (
              <div className="w-3 h-3 border border-violet-300 border-t-violet-600 rounded-full animate-spin"></div>
            )}
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-violet-500 to-violet-600 h-2.5 rounded-full transition-all duration-700 ease-out"
            style={{ width: `${completionRate}%` }}
          ></div>
        </div>
      </div>

      {statistics.tasks_by_priority && (
        <div className="border-t border-gray-100 pt-3 mt-3">
          <h3 className="text-sm font-medium text-gray-700 mb-2">By Priority</h3>
          <div className="grid grid-cols-4 gap-2 text-center text-xs">
            <div className="bg-green-100 text-green-800 p-1 rounded">
              <div>{statistics.tasks_by_priority.low}</div>
              <div>Low</div>
            </div>
            <div className="bg-yellow-100 text-yellow-800 p-1 rounded">
              <div>{statistics.tasks_by_priority.medium}</div>
              <div>Medium</div>
            </div>
            <div className="bg-orange-100 text-orange-800 p-1 rounded">
              <div>{statistics.tasks_by_priority.high}</div>
              <div>High</div>
            </div>
            <div className="bg-red-100 text-red-800 p-1 rounded">
              <div>{statistics.tasks_by_priority.urgent}</div>
              <div>Urgent</div>
            </div>
          </div>
        </div>
      )}

      {(statistics.tasks_due_today !== undefined || statistics.tasks_due_this_week !== undefined) && (
        <div className="border-t border-gray-100 pt-3 mt-3 grid grid-cols-2 gap-3 text-center">
          {statistics.tasks_due_today !== undefined && (
            <div className="bg-blue-50 p-2 rounded">
              <div className="text-sm font-medium text-blue-700">{statistics.tasks_due_today}</div>
              <div className="text-xs text-blue-600">Due Today</div>
            </div>
          )}
          {statistics.tasks_due_this_week !== undefined && (
            <div className="bg-indigo-50 p-2 rounded">
              <div className="text-sm font-medium text-indigo-700">{statistics.tasks_due_this_week}</div>
              <div className="text-xs text-indigo-600">Due This Week</div>
            </div>
          )}
        </div>
      )}

      {/* Show high priority tasks info since backend provides this */}
      <div className="border-t border-gray-100 pt-3 mt-3">
        <div className="bg-orange-50 p-3 rounded-lg text-center">
          <div className="text-xl font-bold text-orange-700">{statistics.high_priority_tasks}</div>
          <div className="text-sm text-orange-600">High Priority Tasks</div>
        </div>
      </div>
    </div>
  );
};

export default TaskStatistics;
