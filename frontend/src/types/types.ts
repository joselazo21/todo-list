// Common interfaces for the application

export interface ITodo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ITodoFilters {
  completed?: boolean;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  overdue?: boolean;
  due_date_from?: string;
  due_date_to?: string;
  search?: string;
  ordering?: string;
}

export interface ITaskStatistics {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  high_priority_tasks: number;
  completion_rate: number;
  // Optional fields that may not be provided by backend
  tasks_by_priority?: {
    low: number;
    medium: number;
    high: number;
    urgent: number;
  };
  tasks_due_today?: number;
  tasks_due_this_week?: number;
}

export interface IProductivityMetrics {
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  average_completion_time: number;
  productivity_score: number;
}

export interface IUser {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface IAuthResponse {
  access: string;
  refresh: string;
  user: IUser;
}
