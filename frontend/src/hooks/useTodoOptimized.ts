import { useState, useCallback } from 'react';
import { useTodoContext } from '../contexts/TodoContext';
import { type ITodo, type ITodoFilters } from '../services/todoService';

const MAX_TODO_LENGTH = 80;

export const useTodoOptimized = () => {
  const todoContext = useTodoContext();
  
  // Local UI state
  const [input, setInput] = useState('');
  const [inputPriority, setInputPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [editId, setEditId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [editPriority, setEditPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');

  // Add todo with optimistic UI updates
  const handleAdd = useCallback(async () => {
    if (input.trim() === '' || input.length > MAX_TODO_LENGTH) return;
    
    try {
      await todoContext.addTodo({
        title: input.trim(),
        completed: false,
        priority: inputPriority
      });
      
      // Reset form
      setInput('');
      setInputPriority('medium');
    } catch (error) {
      // Error is handled by the context
      console.error('Failed to add todo:', error);
    }
  }, [input, inputPriority, todoContext.addTodo]);

  // Delete todo with optimistic UI updates
  const handleDelete = useCallback(async (id: string) => {
    try {
      await todoContext.deleteTodo(id);
    } catch (error) {
      // Error is handled by the context
      console.error('Failed to delete todo:', error);
    }
  }, [todoContext.deleteTodo]);

  // Toggle todo with optimistic UI updates
  const handleToggle = useCallback(async (id: string) => {
    try {
      await todoContext.toggleTodo(id);
    } catch (error) {
      // Error is handled by the context
      console.error('Failed to toggle todo:', error);
    }
  }, [todoContext.toggleTodo]);

  // Start editing
  const handleEdit = useCallback((id: string, title: string, priority: 'low' | 'medium' | 'high' | 'urgent') => {
    setEditId(id);
    setEditText(title);
    setEditPriority(priority);
  }, []);

  // Save edit with optimistic UI updates
  const handleEditSave = useCallback(async (id: string) => {
    if (editText.trim() === '' || editText.length > MAX_TODO_LENGTH) return;
    
    try {
      await todoContext.updateTodo(id, { 
        title: editText.trim(),
        priority: editPriority
      });
      
      // Reset edit state
      setEditId(null);
      setEditText('');
      setEditPriority('medium');
    } catch (error) {
      // Error is handled by the context
      console.error('Failed to update todo:', error);
    }
  }, [editText, editPriority, todoContext.updateTodo]);

  // Cancel edit
  const handleEditCancel = useCallback(() => {
    setEditId(null);
    setEditText('');
    setEditPriority('medium');
  }, []);

  // Apply filters
  const applyFilters = useCallback((filters: ITodoFilters) => {
    todoContext.applyFilters(filters);
  }, [todoContext.applyFilters]);

  // Bulk complete with optimistic UI updates
  const handleBulkComplete = useCallback(async (ids: string[]) => {
    try {
      await todoContext.bulkComplete(ids);
    } catch (error) {
      // Error is handled by the context
      console.error('Failed to bulk complete todos:', error);
    }
  }, [todoContext.bulkComplete]);

  // Refresh todos (useful for pull-to-refresh or manual refresh)
  const refreshTodos = useCallback(async () => {
    await todoContext.loadTodos();
  }, [todoContext.loadTodos]);

  return {
    // Data from context
    todos: todoContext.filteredTodos, // Use filtered todos for display
    allTodos: todoContext.todos, // Access to all todos if needed
    loading: todoContext.loading,
    error: todoContext.error,
    isInitialized: todoContext.isInitialized,
    refreshTrigger: todoContext.refreshTrigger,
    currentFilters: todoContext.currentFilters,
    
    // Local UI state
    input,
    setInput,
    inputPriority,
    setInputPriority,
    editId,
    editText,
    setEditText,
    editPriority,
    setEditPriority,
    
    // Actions
    handleAdd,
    handleDelete,
    handleToggle,
    handleEdit,
    handleEditSave,
    handleEditCancel,
    handleBulkComplete,
    applyFilters,
    refreshTodos,
    
    // Utilities
    MAX_TODO_LENGTH,
  };
};