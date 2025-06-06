import { useState, useEffect, useCallback, useRef } from 'react';
import todoService, {type ITodo, type ITodoFilters } from '../services/todoService';


const MAX_TODO_LENGTH = 80;



export const useTodo = () => {
  const [todos, setTodos] = useState<ITodo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [inputPriority, setInputPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [editId, setEditId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [editPriority, setEditPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [filters, setFilters] = useState<ITodoFilters>({});
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Debounced refresh trigger to avoid too many rapid updates
  const triggerStatsRefresh = useCallback(() => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }
    refreshTimeoutRef.current = setTimeout(() => {
      setRefreshTrigger(prev => prev + 1);
    }, 300); // 300ms debounce
  }, []);

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await todoService.getTodos(filters);
      setTodos(data);
    } catch (err) {
      console.error('Failed to fetch todos:', err);
      setError('Failed to fetch todos. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [filters]);


  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, []);


  const handleAdd = async () => {
    if (input.trim() === '' || input.length > MAX_TODO_LENGTH) return;
    setLoading(true);
    setError(null);
    try {
      await todoService.createTodo({
        title: input.trim(),
        completed: false,
        priority: inputPriority
      });
      setInput('');
      setInputPriority('medium'); // Reset to default
      // Refetch to ensure consistency
      await fetchTodos();
      triggerStatsRefresh(); // Trigger statistics refresh
    } catch (err) {
      console.error('Failed to add todo:', err);
      setError('Failed to add todo. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  const handleDelete = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await todoService.deleteTodo(id);
      // Refetch to ensure consistency
      await fetchTodos();
      triggerStatsRefresh(); // Trigger statistics refresh
    } catch (err) {
      console.error('Failed to delete todo:', err);
      setError('Failed to delete todo. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  const handleToggle = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const todoToToggle = todos.find(todo => todo.id === id);
      if (!todoToToggle) return;

      await todoService.toggleTodo(id, !todoToToggle.completed);
      // Refetch to ensure consistency
      await fetchTodos();
      triggerStatsRefresh(); // Trigger statistics refresh
    } catch (err) {
      console.error('Failed to toggle todo:', err);
      setError('Failed to update todo. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  const handleEdit = (id: string, title: string, priority: 'low' | 'medium' | 'high' | 'urgent') => {
    setEditId(id);
    setEditText(title);
    setEditPriority(priority);
  };


  const handleEditSave = async (id: string) => {
    if (editText.trim() === '' || editText.length > MAX_TODO_LENGTH) return;
    setLoading(true);
    setError(null);
    try {
      await todoService.updateTodo(id, { 
        title: editText.trim(),
        priority: editPriority
      });
      setEditId(null);
      setEditText('');
      setEditPriority('medium');
      // Refetch to ensure consistency
      await fetchTodos();
      triggerStatsRefresh(); // Trigger statistics refresh
    } catch (err) {
      console.error('Failed to update todo:', err);
      setError('Failed to update todo. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  const applyFilters = useCallback((newFilters: ITodoFilters) => {
    // Replace filters completely instead of merging to avoid stale filters
    setFilters(newFilters);
  }, []);


  const handleBulkComplete = async (ids: string[]) => {
    setLoading(true);
    setError(null);
    try {
      await todoService.bulkComplete(ids);
      // Refetch to get updated data
      await fetchTodos();
      triggerStatsRefresh(); // Trigger statistics refresh
    } catch (err) {
      console.error('Failed to bulk complete todos:', err);
      setError('Failed to update todos. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return {
    todos,
    loading,
    error,
    input,
    setInput,
    inputPriority,
    setInputPriority,
    editId,
    editText,
    setEditText,
    editPriority,
    setEditPriority,
    filters,
    refreshTrigger,
    handleAdd,
    handleDelete,
    handleToggle,
    handleEdit,
    handleEditSave,
    applyFilters,
    handleBulkComplete,
    MAX_TODO_LENGTH,
  };
};

