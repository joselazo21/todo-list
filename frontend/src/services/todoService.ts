import api from './api';
import {type ITodo, type ITodoFilters, type IProductivityMetrics } from '../types/types.ts';


export type { ITodo, ITodoFilters, IProductivityMetrics };

// Backend task interface
interface BackendTask {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  due_date?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  is_overdue: boolean;
  days_until_due?: number;
}

// Convert backend task to frontend todo
const backendToFrontend = (task: BackendTask): ITodo => ({
  id: task.id,
  title: task.title,
  description: task.description,
  completed: task.status === 'completed',
  priority: task.priority,
  due_date: task.due_date,
  completed_at: task.completed_at,
  created_at: task.created_at,
  updated_at: task.updated_at,
});

// Convert frontend todo to backend task data
const frontendToBackend = (todo: Partial<ITodo>) => {
  const backendData: any = {};
  
  // Only include fields that the backend expects
  if (todo.title !== undefined) {
    backendData.title = todo.title;
  }
  
  if (todo.description !== undefined) {
    backendData.description = todo.description;
  }
  
  if (todo.priority !== undefined) {
    backendData.priority = todo.priority;
  }
  
  if (todo.completed !== undefined) {
    backendData.status = todo.completed ? 'completed' : 'pending';
  }
  
  if (todo.due_date !== undefined) {
    backendData.due_date = todo.due_date;
  }
  
  return backendData;
};

const todoService = {

  getTodos: async (filters?: ITodoFilters) => {
    const params = new URLSearchParams();

    if (filters) {
      if (filters.completed !== undefined) {
        params.append('status', filters.completed ? 'completed' : 'pending');
      }
      // Note: When filters.completed is undefined, no status filter is applied,
      // which should return all tasks regardless of status
      if (filters.priority) {
        params.append('priority', filters.priority);
      }
      if (filters.overdue !== undefined) {
        params.append('overdue', filters.overdue.toString());
      }
      if (filters.due_date_from) {
        params.append('due_date_from', filters.due_date_from);
      }
      if (filters.due_date_to) {
        params.append('due_date_to', filters.due_date_to);
      }
      if (filters.search) {
        params.append('search_term', filters.search);
      }
      if (filters.ordering) {
        params.append('ordering', filters.ordering);
      }
    }

    const response = await api.get('/tasks/', { params });
    return response.data.map(backendToFrontend);
  },

  getTodo: async (id: string) => {
    const response = await api.get(`/tasks/${id}/`);
    return backendToFrontend(response.data);
  },


  createTodo: async (todo: Partial<ITodo>) => {
    const backendData = frontendToBackend(todo);
    const response = await api.post('/tasks/', backendData);
    return backendToFrontend(response.data);
  },


  updateTodo: async (id: string, updates: Partial<ITodo>) => {
    const backendData = frontendToBackend(updates);
    const response = await api.put(`/tasks/${id}/`, backendData);
    return backendToFrontend(response.data);
  },


  deleteTodo: async (id: string) => {
    await api.delete(`/tasks/${id}/`);
    return true;
  },


  bulkComplete: async (ids: string[]) => {
    const response = await api.post('/tasks/bulk-complete/', { task_ids: ids });
    return response.data;
  },


  toggleTodo: async (id: string, completed: boolean) => {
    const backendData = frontendToBackend({ completed });
    console.log('Toggle todo - sending data:', backendData);
    const response = await api.put(`/tasks/${id}/`, backendData);
    return backendToFrontend(response.data);
  },


  getTaskStatistics: async () => {
    const response = await api.get('/tasks/statistics/');
    return response.data;
  },

  getProductivityMetrics: async (days: number = 30) => {
    const response = await api.get(`/tasks/productivity/?days=${days}`);
    return response.data;
  }
};

export default todoService;
