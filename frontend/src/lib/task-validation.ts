/**
 * Validation utilities for task management
 */

/**
 * Validates task title
 */
export const validateTaskTitle = (title: string): {
  isValid: boolean;
  error?: string;
} => {
  if (!title || title.trim() === '') {
    return {
      isValid: false,
      error: 'Task title is required'
    };
  }

  if (title.length > 255) {
    return {
      isValid: false,
      error: 'Task title must be 255 characters or less'
    };
  }

  return {
    isValid: true
  };
};

/**
 * Validates task description
 */
export const validateTaskDescription = (description: string | null): {
  isValid: boolean;
  error?: string;
} => {
  if (description && description.length > 10000) {
    return {
      isValid: false,
      error: 'Task description must be 10000 characters or less'
    };
  }

  return {
    isValid: true
  };
};

/**
 * Validates a complete task
 */
export const validateTask = (
  title: string,
  description: string | null
): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];

  const titleValidation = validateTaskTitle(title);
  if (!titleValidation.isValid) {
    errors.push(titleValidation.error!);
  }

  const descriptionValidation = validateTaskDescription(description);
  if (!descriptionValidation.isValid) {
    errors.push(descriptionValidation.error!);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};