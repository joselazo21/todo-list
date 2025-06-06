import React, { useState, useEffect, useCallback } from 'react';
import { useTodoOptimized } from '../hooks/useTodoOptimized';
import type { ITodo } from '../services/todoService';
import { CheckIcon, DeleteIcon, SaveIcon } from '../assets/icons';
import StatisticsPanel from "./StatisticsPanel.tsx";


const Todo: React.FC = () => {
  const {
    todos,
    loading,
    error,
    isInitialized,
    input,
    setInput,
    inputPriority,
    setInputPriority,
    editId,
    editText,
    setEditText,
    editPriority,
    setEditPriority,
    refreshTrigger,
    handleAdd,
    handleDelete,
    handleToggle,
    handleEdit,
    handleEditSave,
    handleEditCancel,
    handleBulkComplete,
    applyFilters,
    refreshTodos,
    MAX_TODO_LENGTH,
  } = useTodoOptimized();

  const [filterCompleted, setFilterCompleted] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedTodos, setSelectedTodos] = useState<string[]>([]);
  const [showStats, setShowStats] = useState(false);


  const handleFilterChange = useCallback(() => {
    const filters: any = {};

    // Only add completed filter if not 'all'
    if (filterCompleted !== 'all') {
      filters.completed = filterCompleted === 'completed';
    }

    // Only add priority filter if not 'all'
    if (filterPriority !== 'all') {
      filters.priority = filterPriority;
    }

    // Only add search filter if there's a search term
    if (searchQuery.trim()) {
      filters.search = searchQuery.trim();
    }

    applyFilters(filters);
  }, [filterCompleted, filterPriority, searchQuery, applyFilters]);


  const toggleTodoSelection = (id: string) => {
    setSelectedTodos(prev =>
      prev.includes(id)
        ? prev.filter(todoId => todoId !== id)
        : [...prev, id]
    );
  };


  const onBulkComplete = async () => {
    if (selectedTodos.length > 0) {
      await handleBulkComplete(selectedTodos);
      setSelectedTodos([]);
    }
  };

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };


  useEffect(() => {
    // Only apply filters for status and priority changes, not search
    const filters: any = {};

    if (filterCompleted !== 'all') {
      filters.completed = filterCompleted === 'completed';
    }

    if (filterPriority !== 'all') {
      filters.priority = filterPriority;
    }

    applyFilters(filters);
  }, [filterCompleted, filterPriority, applyFilters]);

  useEffect(() => {
    // This effect is for todos, can be used for other side effects if needed
  }, [todos]);

  return (
    <div className="flex flex-col justify-center items-center bg-white px-6 py-8 rounded-3xl border-2 border-gray-100 w-1/2 mx-auto">
      <h2 className="text-3xl mb-4">Your Todos</h2>


      <div className="w-full flex justify-between items-center mb-4">
        <button
          className="text-sm text-gray-600 hover:text-gray-800 flex items-center transition-all duration-200 hover:scale-105 disabled:opacity-50"
          onClick={refreshTodos}
          disabled={loading}
          title="Refresh todos"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
        
        <button
          className="text-sm text-violet-600 hover:text-violet-800 flex items-center transition-all duration-200 hover:scale-105"
          onClick={() => setShowStats(!showStats)}
        >
          {showStats ? 'Hide Analytics' : 'Show Analytics'}
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </button>
      </div>


      {showStats && <StatisticsPanel refreshTrigger={refreshTrigger} />}

      <div className="w-full mt-2">
        <div className="bg-white rounded-xl border-2 border-gray-100 p-4 mb-4 shadow-sm">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Add New Task</h3>
          <div className="flex flex-col gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Task Title</label>
              <input
                className="w-full border-2 border-gray-200 rounded-lg p-3 bg-transparent focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-violet-400 transition-all"
                type="text"
                placeholder={`Enter your task... (max ${MAX_TODO_LENGTH} chars)`}
                value={input}
                maxLength={MAX_TODO_LENGTH}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
                disabled={loading}
              />
              <div className="text-xs text-gray-500 mt-1">
                {input.length}/{MAX_TODO_LENGTH} characters
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                className="w-full border-2 border-gray-200 rounded-lg p-3 bg-white focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-violet-400 transition-all"
                value={inputPriority}
                onChange={(e) => setInputPriority(e.target.value as 'low' | 'medium' | 'high' | 'urgent')}
                disabled={loading}
              >
                <option value="low">🟢 Low Priority</option>
                <option value="medium">🟡 Medium Priority</option>
                <option value="high">🟠 High Priority</option>
                <option value="urgent">🔴 Urgent Priority</option>
              </select>
            </div>
            <button
              className="w-full bg-violet-500 hover:bg-violet-600 text-white text-lg px-4 py-3 rounded-lg font-bold transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-violet-400 disabled:opacity-50 disabled:transform-none disabled:bg-gray-300"
              onClick={handleAdd}
              disabled={loading || !input.trim()}
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Adding Task...
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Task
                </div>
              )}
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mt-4 pb-4 border-b border-gray-100">
          <div className="flex items-center">
            <label className="mr-2 text-sm text-gray-600">Status:</label>
            <select
              className="border border-gray-200 rounded-md p-1 text-sm"
              value={filterCompleted}
              onChange={(e) => setFilterCompleted(e.target.value)}
              disabled={loading}
            >
              <option value="all">All</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div className="flex items-center">
            <label className="mr-2 text-sm text-gray-600">Priority:</label>
            <select
              className="border border-gray-200 rounded-md p-1 text-sm"
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              disabled={loading}
            >
              <option value="all">All</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div className="flex items-center flex-grow">
            <input
              className="ml-auto border border-gray-200 rounded-md p-1 text-sm w-full max-w-[180px]"
              type="search"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                // Auto-apply filter when search is cleared
                if (!e.target.value.trim()) {
                  handleFilterChange();
                }
              }}
              onKeyDown={(e) => e.key === 'Enter' && handleFilterChange()}
              disabled={loading}
            />
            <button
              className="ml-1 bg-gray-100 px-2 py-1 rounded text-sm hover:bg-gray-200"
              onClick={handleFilterChange}
              disabled={loading}
            >
              Search
            </button>
          </div>
        </div>


        {!loading && todos.length > 0 && (
          <div className="flex items-center justify-between mt-4 pb-2">
            <div className="flex items-center">
              <span className="text-sm text-gray-600 mr-2">
                {selectedTodos.length > 0
                  ? `${selectedTodos.length} task${selectedTodos.length > 1 ? 's' : ''} selected`
                  : 'Select tasks for bulk actions'}
              </span>
            </div>
            {selectedTodos.length > 0 && (
              <div className="flex gap-2">
                <button
                  className="bg-green-500 hover:bg-green-600 text-white text-sm px-3 py-1 rounded transition-colors"
                  onClick={onBulkComplete}
                  disabled={loading}
                >
                  Complete Selected
                </button>
                <button
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm px-3 py-1 rounded transition-colors"
                  onClick={() => setSelectedTodos([])}
                  disabled={loading}
                >
                  Clear Selection
                </button>
              </div>
            )}
          </div>
        )}


        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mt-4" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {loading && !isInitialized && (
          <div className="space-y-2 mt-4">
            {/* Skeleton loader */}
            {[...Array(3)].map((_, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 rounded-xl px-3 py-2 shadow-sm border border-gray-100 animate-pulse">
                <div className="flex items-center gap-3 w-full">
                  <div className="flex items-center">
                    <div className="w-4 h-4 bg-gray-200 rounded mr-2"></div>
                    <div className="w-5 h-5 bg-gray-200 rounded-full"></div>
                  </div>
                  <div className="flex-1 flex flex-col">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/4"></div>
                  </div>
                </div>
                <div className="w-8 h-8 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        )}

        {(isInitialized || !loading) && (
          <ul className="space-y-2 mt-4">
            {todos.map((todo: ITodo) => (
              <li
                key={todo.id}
                className={`flex items-center justify-between bg-gray-50 rounded-xl px-3 py-2 shadow-sm border ${
                  selectedTodos.includes(todo.id) ? 'border-violet-400 bg-violet-50' : 'border-gray-100'
                }`}
              >
                <div className="flex items-center gap-3 w-full">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      className="mr-2 h-4 w-4 text-violet-500 border-gray-300 rounded focus:ring-violet-400"
                      checked={selectedTodos.includes(todo.id)}
                      onChange={() => toggleTodoSelection(todo.id)}
                    />
                    <button
                      onClick={() => handleToggle(todo.id)}
                      className={`w-5 h-5 flex items-center justify-center border-2 rounded-full transition-all duration-200 ${todo.completed ? 'bg-violet-100 border-violet-500' : 'border-gray-300 bg-white hover:border-violet-400'}`}
                      aria-label="Toggle complete"
                      disabled={loading}
                    >
                      {todo.completed && <CheckIcon />}
                    </button>
                  </div>

                  {editId === todo.id ? (
                    <div className="flex-1 bg-white rounded-lg border-2 border-violet-200 p-3 shadow-sm">
                      <div className="flex flex-col gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Task Title</label>
                          <input
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent text-gray-800 transition-all"
                            value={editText}
                            maxLength={MAX_TODO_LENGTH}
                            onChange={(e) => setEditText(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleEditSave(todo.id)}
                            autoFocus
                            disabled={loading}
                            placeholder="Enter task title..."
                          />
                          <div className="text-xs text-gray-500 mt-1">
                            {editText.length}/{MAX_TODO_LENGTH} characters
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Priority</label>
                          <select
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent transition-all"
                            value={editPriority}
                            onChange={(e) => setEditPriority(e.target.value as 'low' | 'medium' | 'high' | 'urgent')}
                            disabled={loading}
                          >
                            <option value="low">🟢 Low Priority</option>
                            <option value="medium">🟡 Medium Priority</option>
                            <option value="high">🟠 High Priority</option>
                            <option value="urgent">🔴 Urgent Priority</option>
                          </select>
                        </div>
                        <div className="flex gap-2 pt-2">
                          <button
                            className="flex-1 bg-violet-500 hover:bg-violet-600 text-white px-3 py-2 rounded-lg font-medium transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-violet-400 disabled:opacity-50 disabled:transform-none"
                            onClick={() => handleEditSave(todo.id)}
                            disabled={loading || !editText.trim()}
                          >
                            {loading ? (
                              <div className="flex items-center justify-center gap-2">
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                Saving...
                              </div>
                            ) : (
                              <div className="flex items-center justify-center gap-2">
                                <SaveIcon />
                                Save Changes
                              </div>
                            )}
                          </button>
                          <button
                            className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-400"
                            onClick={handleEditCancel}
                            disabled={loading}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1 flex flex-col">
                      <span
                        className={`text-gray-800 text-base cursor-pointer ${todo.completed ? 'line-through text-gray-400' : ''}`}
                        onClick={() => handleEdit(todo.id, todo.title, todo.priority)}
                      >
                        {todo.title}
                      </span>
                      {todo.description && (
                        <span className="text-xs text-gray-500 mt-1">{todo.description}</span>
                      )}
                      <div className="flex items-center mt-1 gap-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getPriorityBadgeClass(todo.priority)}`}>
                          {todo.priority}
                        </span>
                        {todo.due_date && (
                          <span className="text-xs text-gray-500">
                            Due: {new Date(todo.due_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {editId !== todo.id && (
                  <div className="flex gap-1 items-center">
                    <button
                      className="p-2 rounded-lg hover:bg-red-100 transition-all duration-200 disabled:opacity-50 text-red-600 hover:text-red-700"
                      onClick={() => handleDelete(todo.id)}
                      title="Delete Task"
                      disabled={loading}
                    >
                      <DeleteIcon />
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}


        {isInitialized && todos.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-400 mb-2">No todos found.</p>
            <p className="text-sm text-gray-400">
              {filterCompleted !== 'all' || filterPriority !== 'all' || searchQuery
                ? "Try changing your filters or search query."
                : "Add your first todo above!"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Todo;

