import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode, useMemo } from 'react';
import todoService, { type ITodo, type ITodoFilters } from '../services/todoService';
import { useAuth } from './AuthContext';

interface TodoContextType {
  // State
  todos: ITodo[];
  filteredTodos: ITodo[];
  loading: boolean;
  error: string | null;
  isInitialized: boolean;
  
  // Actions
  loadTodos: () => Promise<void>;
  addTodo: (todo: Partial<ITodo>) => Promise<ITodo>;
  updateTodo: (id: string, updates: Partial<ITodo>) => Promise<ITodo>;
  deleteTodo: (id: string) => Promise<void>;
  toggleTodo: (id: string) => Promise<ITodo>;
  bulkComplete: (ids: string[]) => Promise<void>;
  
  // Filters
  applyFilters: (filters: ITodoFilters) => void;
  clearFilters: () => void;
  currentFilters: ITodoFilters;
  
  // Statistics trigger
  refreshTrigger: number;
}

const TodoContext = createContext<TodoContextType | undefined>(undefined);

interface TodoProviderProps {
  children: ReactNode;
}

export const TodoProvider: React.FC<TodoProviderProps> = ({ children }) => {
  const auth = useAuth();
  const [todos, setTodos] = useState<ITodo[]>([]);
  const [filteredTodos, setFilteredTodos] = useState<ITodo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [currentFilters, setCurrentFilters] = useState<ITodoFilters>({});
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Apply filters to todos
  const applyFiltersToTodos = useCallback((todosToFilter: ITodo[], filters: ITodoFilters) => {
    let filtered = [...todosToFilter];

    // Filter by completion status
    if (filters.completed !== undefined) {
      filtered = filtered.filter(todo => todo.completed === filters.completed);
    }

    // Filter by priority
    if (filters.priority) {
      filtered = filtered.filter(todo => todo.priority === filters.priority);
    }

    // Filter by search term
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filtered = filtered.filter(todo => 
        todo.title.toLowerCase().includes(searchTerm) ||
        (todo.description && todo.description.toLowerCase().includes(searchTerm))
      );
    }

    // Filter by overdue status
    if (filters.overdue !== undefined) {
      const now = new Date();
      filtered = filtered.filter(todo => {
        if (!todo.due_date) return !filters.overdue;
        const dueDate = new Date(todo.due_date);
        const isOverdue = dueDate < now && !todo.completed;
        return filters.overdue ? isOverdue : !isOverdue;
      });
    }

    // Filter by date range
    if (filters.due_date_from || filters.due_date_to) {
      filtered = filtered.filter(todo => {
        if (!todo.due_date) return false;
        const dueDate = new Date(todo.due_date);
        
        if (filters.due_date_from) {
          const fromDate = new Date(filters.due_date_from);
          if (dueDate < fromDate) return false;
        }
        
        if (filters.due_date_to) {
          const toDate = new Date(filters.due_date_to);
          if (dueDate > toDate) return false;
        }
        
        return true;
      });
    }

    // Apply ordering
    if (filters.ordering) {
      filtered.sort((a, b) => {
        switch (filters.ordering) {
          case 'created_at':
            return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          case '-created_at':
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          case 'priority':
            const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
          case '-priority':
            const priorityOrderDesc = { urgent: 4, high: 3, medium: 2, low: 1 };
            return priorityOrderDesc[b.priority] - priorityOrderDesc[a.priority];
          case 'due_date':
            if (!a.due_date && !b.due_date) return 0;
            if (!a.due_date) return 1;
            if (!b.due_date) return -1;
            return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
          case '-due_date':
            if (!a.due_date && !b.due_date) return 0;
            if (!a.due_date) return -1;
            if (!b.due_date) return 1;
            return new Date(b.due_date).getTime() - new Date(a.due_date).getTime();
          default:
            return 0;
        }
      });
    }

    return filtered;
  }, []);

  // Update filtered todos when todos or filters change
  useEffect(() => {
    const filtered = applyFiltersToTodos(todos, currentFilters);
    setFilteredTodos(filtered);
  }, [todos, currentFilters, applyFiltersToTodos]);

  // Load todos from API
  const loadTodos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Load all todos without filters to have complete dataset
      const data = await todoService.getTodos();
      setTodos(data);
      setIsInitialized(true);
    } catch (err: any) {
      console.error('Failed to fetch todos:', err);
      
      // Handle authentication errors specifically
      if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
        // Don't set isInitialized to true on auth errors
      } else {
        setError('Failed to fetch todos. Please try again.');
        setIsInitialized(true); // Still mark as initialized for other errors
      }
    } finally {
      setLoading(false);
    }
  }, []); // Remove loading dependency to prevent infinite loop

  // Initialize todos on mount - only when auth is ready and user is authenticated
  useEffect(() => {
    if (!auth.isLoading && auth.isAuthenticated && !isInitialized && !loading) {
      loadTodos();
    }
  }, [auth.isLoading, auth.isAuthenticated, isInitialized, loading, loadTodos]);

  // Clear todos when user logs out
  useEffect(() => {
    if (!auth.isAuthenticated && isInitialized) {
      setTodos([]);
      setFilteredTodos([]);
      setIsInitialized(false);
      setError(null);
    }
  }, [auth.isAuthenticated, isInitialized]);

  // Trigger statistics refresh
  const triggerStatsRefresh = useCallback(() => {
    setRefreshTrigger(prev => prev + 1);
  }, []);

  // Add todo
  const addTodo = useCallback(async (todoData: Partial<ITodo>): Promise<ITodo> => {
    setLoading(true);
    setError(null);
    try {
      const newTodo = await todoService.createTodo(todoData);
      setTodos(prev => [newTodo, ...prev]); // Add to beginning for better UX
      triggerStatsRefresh();
      return newTodo;
    } catch (err) {
      console.error('Failed to add todo:', err);
      setError('Failed to add todo. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [triggerStatsRefresh]);

  // Update todo
  const updateTodo = useCallback(async (id: string, updates: Partial<ITodo>): Promise<ITodo> => {
    setLoading(true);
    setError(null);
    try {
      const updatedTodo = await todoService.updateTodo(id, updates);
      setTodos(prev => prev.map(todo => 
        todo.id === id ? updatedTodo : todo
      ));
      triggerStatsRefresh();
      return updatedTodo;
    } catch (err) {
      console.error('Failed to update todo:', err);
      setError('Failed to update todo. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [triggerStatsRefresh]);

  // Delete todo
  const deleteTodo = useCallback(async (id: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await todoService.deleteTodo(id);
      setTodos(prev => prev.filter(todo => todo.id !== id));
      triggerStatsRefresh();
    } catch (err) {
      console.error('Failed to delete todo:', err);
      setError('Failed to delete todo. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [triggerStatsRefresh]);

  // Toggle todo completion
  const toggleTodo = useCallback(async (id: string): Promise<ITodo> => {
    // Optimistic update
    const todoToToggle = todos.find(todo => todo.id === id);
    if (!todoToToggle) throw new Error('Todo not found');

    const optimisticUpdate = { ...todoToToggle, completed: !todoToToggle.completed };
    setTodos(prev => prev.map(todo => 
      todo.id === id ? optimisticUpdate : todo
    ));

    setLoading(true);
    setError(null);
    try {
      const updatedTodo = await todoService.toggleTodo(id, !todoToToggle.completed);
      setTodos(prev => prev.map(todo => 
        todo.id === id ? updatedTodo : todo
      ));
      triggerStatsRefresh();
      return updatedTodo;
    } catch (err) {
      // Revert optimistic update on error
      setTodos(prev => prev.map(todo => 
        todo.id === id ? todoToToggle : todo
      ));
      console.error('Failed to toggle todo:', err);
      setError('Failed to update todo. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [todos, triggerStatsRefresh]);

  // Bulk complete todos
  const bulkComplete = useCallback(async (ids: string[]): Promise<void> => {
    // Optimistic update
    const optimisticTodos = todos.map(todo => 
      ids.includes(todo.id) ? { ...todo, completed: true } : todo
    );
    setTodos(optimisticTodos);

    setLoading(true);
    setError(null);
    try {
      await todoService.bulkComplete(ids);
      // The optimistic update should be correct, but we could refetch if needed
      triggerStatsRefresh();
    } catch (err) {
      // Revert optimistic update on error
      setTodos(todos);
      console.error('Failed to bulk complete todos:', err);
      setError('Failed to update todos. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [todos, triggerStatsRefresh]);

  // Apply filters
  const applyFilters = useCallback((filters: ITodoFilters) => {
    setCurrentFilters(filters);
  }, []);

  // Clear filters
  const clearFilters = useCallback(() => {
    setCurrentFilters({});
  }, []);

  const value: TodoContextType = useMemo(() => ({
    // State
    todos,
    filteredTodos,
    loading,
    error,
    isInitialized,
    
    // Actions
    loadTodos,
    addTodo,
    updateTodo,
    deleteTodo,
    toggleTodo,
    bulkComplete,
    
    // Filters
    applyFilters,
    clearFilters,
    currentFilters,
    
    // Statistics trigger
    refreshTrigger,
  }), [
    todos,
    filteredTodos,
    loading,
    error,
    isInitialized,
    loadTodos,
    addTodo,
    updateTodo,
    deleteTodo,
    toggleTodo,
    bulkComplete,
    applyFilters,
    clearFilters,
    currentFilters,
    refreshTrigger,
  ]);

  return (
    <TodoContext.Provider value={value}>
      {children}
    </TodoContext.Provider>
  );
};

export const useTodoContext = (): TodoContextType => {
  const context = useContext(TodoContext);
  if (context === undefined) {
    throw new Error('useTodoContext must be used within a TodoProvider');
  }
  return context;
};