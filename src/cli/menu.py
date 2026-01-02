"""Menu and input handling functions for the CLI."""


def prompt_task_input() -> tuple[str, str]:
    """Collect task title and description from user with validation.

    Loops until valid title is provided (non-empty, ≤200 chars).
    Description is optional and must be ≤2000 chars.

    Returns:
        Tuple of (title, description)
    """
    # Get title with validation loop
    while True:
        title = input("Enter task title: ").strip()

        if not title:
            print("[ERROR] Title cannot be empty. Please try again.")
            continue

        if len(title) > 200:
            print("[ERROR] Title must be 200 characters or less.")
            continue

        break

    # Get description with validation
    while True:
        description = input("Enter task description (optional, press Enter to skip): ").strip()

        if len(description) > 2000:
            print("[ERROR] Description must be 2000 characters or less.")
            continue

        break

    return title, description


def display_menu() -> None:
    """Display the main menu options."""
    print("\n=== Todo Application ===")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. View Task Details")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Toggle Complete")
    print("0. Exit")


def get_menu_choice() -> str:
    """Get and validate menu selection from user.

    Returns:
        User's menu choice as a string
    """
    return input("\nSelect option: ").strip()


def prompt_task_id(prompt_message: str) -> int | None:
    """Get and validate task ID input from user.

    Args:
        prompt_message: The prompt message to display

    Returns:
        Task ID as integer, or None if input is invalid
    """
    try:
        task_id = int(input(prompt_message).strip())
        return task_id
    except ValueError:
        return None


def prompt_task_update(
    current_title: str, current_description: str
) -> tuple[str | None, str | None]:
    """Get new title and/or description for task update.

    Displays current values and allows user to press Enter to keep them.
    Validates new values if provided.

    Args:
        current_title: Current task title
        current_description: Current task description

    Returns:
        Tuple of (new_title or None, new_description or None)
    """
    print("\nCurrent Task:")
    print(f"  Title: {current_title}")
    print(f"  Description: {current_description if current_description else '(none)'}")

    # Get new title
    new_title: str | None = None
    while True:
        title_input = input(f'Enter new title (or press Enter to keep "{current_title}"): ').strip()

        if not title_input:
            # User pressed Enter - keep current title
            break

        if len(title_input) > 200:
            print("[ERROR] Title must be 200 characters or less.")
            continue

        new_title = title_input
        break

    # Get new description
    new_description: str | None = None
    while True:
        desc_input = input(
            f'Enter new description (or press Enter to keep "{current_description}"): '
        ).strip()

        if not desc_input:
            # User pressed Enter - keep current description
            break

        if len(desc_input) > 2000:
            print("[ERROR] Description must be 2000 characters or less.")
            continue

        new_description = desc_input
        break

    return new_title, new_description


def confirm_deletion(task_title: str) -> bool:
    """Prompt user to confirm task deletion.

    Args:
        task_title: Title of the task to be deleted

    Returns:
        True if user confirms, False if user cancels
    """
    while True:
        response = input(f'Delete task "{task_title}"? (y/n): ').strip().lower()

        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            print("[ERROR] Please enter 'y' or 'n'.")
