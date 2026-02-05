'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import TaskItem from './TaskItem';
import UserFriendlyError from '../UserFriendlyError';

interface Task {
  id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const data = await apiClient.get('/tasks');
      setTasks(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks. Please try again.');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskToggle = async (taskId: string, currentStatus: boolean) => {
    try {
      const updatedTask = await apiClient.patch(`/tasks/${taskId}/complete`, {});
      setTasks(tasks.map(task =>
        task.id === taskId ? { ...task, is_completed: !currentStatus } : task
      ));
    } catch (err: any) {
      setError(err.message || 'Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    }
  };

  const handleTaskDelete = async (taskId: string) => {
    try {
      await apiClient.delete(`/tasks/${taskId}`);
      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete task. Please try again.');
      console.error('Error deleting task:', err);
    }
  };

  const handleTaskUpdate = async (taskId: string, updatedData: Partial<Task>) => {
    try {
      const updatedTask = await apiClient.put(`/tasks/${taskId}`, updatedData);
      setTasks(tasks.map(task =>
        task.id === taskId ? { ...task, ...updatedTask } : task
      ));
    } catch (err: any) {
      setError(err.message || 'Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    }
  };

  const dismissError = () => {
    setError(null);
  };

  if (loading) {
    return (
      <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-2xl border border-gray-700/50 mb-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-600 rounded w-1/4 mb-4"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-700/50 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-2xl border border-gray-700/50 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-medium text-white">Your Tasks</h2>
        <span className="text-sm text-gray-400">
          {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
        </span>
      </div>

      {error && (
        <UserFriendlyError
          message={error}
          onClose={dismissError}
          variant="error"
        />
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-400">No tasks yet. Create your first task!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={() => handleTaskToggle(task.id, task.is_completed)}
              onDelete={() => handleTaskDelete(task.id)}
              onUpdate={(updatedData) => handleTaskUpdate(task.id, updatedData)}
            />
          ))}
        </div>
      )}
    </div>
  );
}