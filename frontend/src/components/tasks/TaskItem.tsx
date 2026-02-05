'use client';

import { useState } from 'react';
import { TrashIcon, PencilIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface Task {
  id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

interface TaskItemProps {
  task: Task;
  onToggle: () => void;
  onDelete: () => void;
  onUpdate: (updatedData: Partial<Task>) => void;
}

export default function TaskItem({ task, onToggle, onDelete, onUpdate }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');

  const handleSave = () => {
    onUpdate({
      title: editTitle,
      description: editDescription || null
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setIsEditing(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`border rounded-lg p-4 ${task.is_completed ? 'bg-gray-700/30 border-green-500/30' : 'bg-gray-800/30 border-gray-700/50'}`}>
      {isEditing ? (
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full border border-gray-600 rounded-md px-3 py-1 text-lg font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-700/50 text-white"
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            rows={2}
            className="w-full border border-gray-600 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-700/50 text-white"
          />
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="inline-flex items-center px-3 py-1 border border-gray-600 text-sm font-medium rounded-md shadow-sm text-gray-300 bg-gray-700 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-start">
            <button
              onClick={onToggle}
              className={`mr-3 mt-1 ${task.is_completed ? 'text-green-400' : 'text-gray-400'} hover:text-green-300`}
              aria-label={task.is_completed ? 'Mark as incomplete' : 'Mark as complete'}
            >
              {task.is_completed ? (
                <CheckCircleIcon className="h-5 w-5" />
              ) : (
                <XCircleIcon className="h-5 w-5" />
              )}
            </button>
            <div className="flex-1">
              <h3 className={`text-lg font-medium ${task.is_completed ? 'line-through text-gray-400' : 'text-white'}`}>
                {task.title}
              </h3>
              {task.description && (
                <p className={`mt-1 text-gray-300 ${task.is_completed ? 'line-through' : ''}`}>
                  {task.description}
                </p>
              )}
              <p className="mt-2 text-xs text-gray-500">
                Created: {formatDate(task.created_at)}
                {task.created_at !== task.updated_at && ` • Updated: ${formatDate(task.updated_at)}`}
              </p>
            </div>
            <div className="flex space-x-2 ml-2">
              <button
                onClick={() => setIsEditing(true)}
                className="text-gray-400 hover:text-indigo-400"
                aria-label="Edit task"
              >
                <PencilIcon className="h-5 w-5" />
              </button>
              <button
                onClick={onDelete}
                className="text-gray-400 hover:text-red-400"
                aria-label="Delete task"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}