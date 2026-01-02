"""Main entry point for the console todo application."""

from src.cli.display import (
    format_error,
    format_success,
    format_task_details,
    format_task_list,
)
from src.cli.menu import (
    confirm_deletion,
    display_menu,
    get_menu_choice,
    prompt_task_id,
    prompt_task_input,
    prompt_task_update,
)
from src.services.task_manager import TaskManager


def handle_add_task(manager: TaskManager) -> None:
    """Handle adding a new task.

    Args:
        manager: The TaskManager instance
    """
    try:
        title, description = prompt_task_input()
        task = manager.add_task(title, description)
        print(f"\n{format_success(f'Task added successfully! (ID: {task.id})')}")
    except ValueError as e:
        print(f"\n{format_error(f'Error: {str(e)}')}")


def handle_view_all_tasks(manager: TaskManager) -> None:
    """Handle viewing all tasks.

    Args:
        manager: The TaskManager instance
    """
    tasks = manager.list_tasks()
    print(f"\n{format_task_list(tasks)}")


def handle_view_task_details(manager: TaskManager) -> None:
    """Handle viewing details of a specific task.

    Args:
        manager: The TaskManager instance
    """
    task_id = prompt_task_id("Enter task ID to view: ")

    if task_id is None:
        print(f"\n{format_error('Please enter a valid task ID (number).')}")
        return

    task = manager.get_task(task_id)

    if task is None:
        print(f"\n{format_error(f'Task with ID {task_id} not found.')}")
        return

    print(f"\n{format_task_details(task)}")


def handle_update_task(manager: TaskManager) -> None:
    """Handle updating a task.

    Args:
        manager: The TaskManager instance
    """
    task_id = prompt_task_id("Enter task ID to update: ")

    if task_id is None:
        print(f"\n{format_error('Please enter a valid task ID (number).')}")
        return

    task = manager.get_task(task_id)

    if task is None:
        print(f"\n{format_error(f'Task with ID {task_id} not found.')}")
        return

    new_title, new_description = prompt_task_update(task.title, task.description)

    try:
        manager.update_task(task_id, title=new_title, description=new_description)
        print(f"\n{format_success('Task updated successfully!')}")
    except ValueError as e:
        print(f"\n{format_error(f'Error: {str(e)}')}")


def handle_delete_task(manager: TaskManager) -> None:
    """Handle deleting a task.

    Args:
        manager: The TaskManager instance
    """
    task_id = prompt_task_id("Enter task ID to delete: ")

    if task_id is None:
        print(f"\n{format_error('Please enter a valid task ID (number).')}")
        return

    task = manager.get_task(task_id)

    if task is None:
        print(f"\n{format_error(f'Task with ID {task_id} not found.')}")
        return

    if confirm_deletion(task.title):
        manager.delete_task(task_id)
        print(f"\n{format_success('Task deleted successfully!')}")
    else:
        print(f"\n{format_error('Deletion cancelled.')}")


def handle_toggle_complete(manager: TaskManager) -> None:
    """Handle toggling task completion status.

    Args:
        manager: The TaskManager instance
    """
    task_id = prompt_task_id("Enter task ID to toggle completion: ")

    if task_id is None:
        print(f"\n{format_error('Please enter a valid task ID (number).')}")
        return

    task = manager.toggle_complete(task_id)

    if task is None:
        print(f"\n{format_error(f'Task with ID {task_id} not found.')}")
        return

    status = "complete" if task.completed else "incomplete"
    print(f"\n{format_success(f'Task marked as {status}!')}")


def handle_exit() -> None:
    """Handle application exit."""
    print("\nThanks for using Todo App! All data will be cleared on exit.")
    print("Goodbye!")


def main() -> None:
    """Main application loop."""
    manager = TaskManager()

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == "1":
            handle_add_task(manager)
        elif choice == "2":
            handle_view_all_tasks(manager)
        elif choice == "3":
            handle_view_task_details(manager)
        elif choice == "4":
            handle_update_task(manager)
        elif choice == "5":
            handle_delete_task(manager)
        elif choice == "6":
            handle_toggle_complete(manager)
        elif choice == "0":
            handle_exit()
            break
        else:
            print(f"\n{format_error('Invalid option. Please try again.')}")


if __name__ == "__main__":
    main()
