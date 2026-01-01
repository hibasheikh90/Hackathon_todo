"""
CLI Menu System for the Todo application.

This module implements the interactive command-line interface with
a main menu loop and handlers for all user operations.
"""

from typing import Optional
from ..core.task_manager import TaskManager
from .display import (
    display_header,
    display_tasks,
    show_success,
    show_error,
    show_info
)
from ..utils.validators import validate_task_id


class TodoCLI:
    """Command-line interface for the Todo application."""

    def __init__(self):
        """Initialize the CLI with a TaskManager instance."""
        self.task_manager = TaskManager()
        self.running = True

    def run(self) -> None:
        """Main application loop."""
        display_header("TODO APP - PHASE I")

        while self.running:
            self._show_menu()
            choice = input("Enter your choice (1-6): ").strip()
            self._handle_choice(choice)

    def _show_menu(self) -> None:
        """Display the main menu options."""
        print("\n" + "-" * 30)
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Task Complete/Incomplete")
        print("6. Exit")
        print("-" * 30)

    def _handle_choice(self, choice: str) -> None:
        """Dispatch user choice to appropriate handler.

        Args:
            choice: User's menu selection (1-6)
        """
        handlers = {
            "1": self._add_task,
            "2": self._view_tasks,
            "3": self._update_task,
            "4": self._delete_task,
            "5": self._toggle_status,
            "6": self._exit_app
        }

        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            show_error("Invalid choice. Please enter a number between 1 and 6.")

    def _add_task(self) -> None:
        """Handle adding a new task."""
        try:
            print("\n--- Add New Task ---")
            title = input("Enter task title: ").strip()
            description = input("Enter description (optional): ").strip()

            task = self.task_manager.add_task(title, description)
            show_success(f"Task added successfully! (ID: {task.id}, Title: \"{task.title}\")")

        except ValueError as e:
            show_error(str(e))

        input("Press Enter to continue...")

    def _view_tasks(self) -> None:
        """Handle viewing all tasks."""
        print("\n--- All Tasks ---")
        tasks = self.task_manager.get_all_tasks()
        display_tasks(tasks)
        input("Press Enter to continue...")

    def _update_task(self) -> None:
        """Handle updating a task."""
        try:
            print("\n--- Update Task ---")
            task_id_str = input("Enter task ID to update: ")
            task_id = validate_task_id(task_id_str)

            # Show current task
            task = self.task_manager.get_task(task_id)
            if not task:
                raise ValueError(f"Task ID {task_id} not found")

            print(f"\nCurrent title: {task.title}")
            print(f"Current description: {task.description or '(none)'}\n")

            new_title = input("Enter new title (press Enter to keep current): ").strip()
            new_desc = input("Enter new description (press Enter to keep current): ").strip()

            # Prepare update arguments
            title_arg = new_title if new_title else None
            desc_arg = new_desc if new_desc else None

            updated_task = self.task_manager.update_task(task_id, title_arg, desc_arg)
            show_success(f"Task updated successfully! (ID: {updated_task.id})")

        except ValueError as e:
            show_error(str(e))

        input("Press Enter to continue...")

    def _delete_task(self) -> None:
        """Handle deleting a task."""
        try:
            print("\n--- Delete Task ---")
            task_id_str = input("Enter task ID to delete: ")
            task_id = validate_task_id(task_id_str)

            # Show task and confirm
            task = self.task_manager.get_task(task_id)
            if not task:
                raise ValueError(f"Task ID {task_id} not found")

            print(f"\nTask to delete: {task.title}")
            confirm = input("Are you sure? (y/n): ").strip().lower()

            if confirm == 'y':
                deleted_task = self.task_manager.delete_task(task_id)
                show_success(f"Task deleted: \"{deleted_task.title}\"")
            else:
                show_info("Deletion cancelled.")

        except ValueError as e:
            show_error(str(e))

        input("Press Enter to continue...")

    def _toggle_status(self) -> None:
        """Handle toggling task completion status."""
        try:
            print("\n--- Toggle Task Status ---")
            task_id_str = input("Enter task ID: ")
            task_id = validate_task_id(task_id_str)

            task = self.task_manager.toggle_status(task_id)
            status = "complete" if task.completed else "incomplete"
            show_success(f"Task marked as {status}: \"{task.title}\"")

        except ValueError as e:
            show_error(str(e))

        input("Press Enter to continue...")

    def _exit_app(self) -> None:
        """Handle application exit."""
        print("\nThank you for using Todo App! Goodbye.\n")
        self.running = False
