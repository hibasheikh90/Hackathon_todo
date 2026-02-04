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
    <div className={`border rounded-lg p-4 ${task.is_completed ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'}`}>
      {isEditing ? (
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-1 text-lg font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            rows={2}
            className="w-full border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
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
              className={`mr-3 mt-1 ${task.is_completed ? 'text-green-500' : 'text-gray-300'} hover:text-green-600`}
              aria-label={task.is_completed ? 'Mark as incomplete' : 'Mark as complete'}
            >
              {task.is_completed ? (
                <CheckCircleIcon className="h-5 w-5" />
              ) : (
                <XCircleIcon className="h-5 w-5" />
              )}
            </button>
            <div className="flex-1">
              <h3 className={`text-lg font-medium ${task.is_completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {task.title}
              </h3>
              {task.description && (
                <p className={`mt-1 text-gray-600 ${task.is_completed ? 'line-through' : ''}`}>
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
                className="text-gray-400 hover:text-indigo-600"
                aria-label="Edit task"
              >
                <PencilIcon className="h-5 w-5" />
              </button>
              <button
                onClick={onDelete}
                className="text-gray-400 hover:text-red-600"
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