"""Handles migration of work items from Azure DevOps to Rado requirements tree."""

from AzureApi.api_service import ApiService
from collections import defaultdict
from typing import List, Dict, Any
import ast


class Migration:
    """Orchestrates the migration of work items from Azure DevOps to Rado."""

    def __init__(self):
        """Initialize the migration service with Azure API client."""
        self._azure_api_service = ApiService()

    def start_migration(self, wi_tuple_id, project_name, target_id, dry_run):
        """
        Orchestrates the complete migration workflow.

        Args:
            wi_tuple_id: Tuple of work item IDs to migrate
            project_name: Name of the Azure DevOps project
            target_id: ID of the target parent item in the tree
            dry_run: If True, simulates the migration without making changes
        """
        # Retrieve project ID from project name
        project_id = self._azure_api_service.get_project_id(project_name=project_name)

        # Fetch work items and their hierarchy
        workitem_json = self._azure_api_service.get_workitem_with_children_recursively(
            wi_tuple_id
        )
        tree_items = self._azure_api_service.get_all_tree_items(project_id) or []

        # Build set of existing tree item IDs for quick lookup
        tree_item_ids = self.get_tree_items_id(tree_items)

        tree_items = tree_items['value'] if "value" in tree_items and isinstance(tree_items,dict) else tree_items

        # If target exists in tree, remove its children to avoid conflicts
        if target_id in tree_item_ids:
            children_to_delete = self.window_by_children(tree_items, target_id)
            wi_tuple_id = self.normalize_wi_ids(wi_tuple_id)
            self.check_if_workitem_to_add_exist_on_tree(
                wi_tuple_id,
                tree_item_ids,
                children_to_delete,
            )

            if children_to_delete:
                self._azure_api_service.delete_tree_item(
                    project_id=project_id,
                    tree_item_list=children_to_delete,
                    dry_run=dry_run,
                )

        # If target is root (-1), remove all existing tree items
        if target_id == "-1" and tree_items:
            self._azure_api_service.delete_tree_item(
                project_id=project_id,
                tree_item_list=tree_items,
                dry_run=dry_run,
            )

        # Add work items to the tree
        self.add_wi_to_tree(workitem_json, project_id, target_id, dry_run)

    def add_wi_to_tree(self, workitem_json, project_id, target_id, dry_run):
        """
        Adds work items and their relationships to the tree.

        Args:
            workitem_json: Work item data including relations
            project_id: Azure DevOps project ID
            target_id: ID of the target parent item
            dry_run: If True, skips actual API calls
        """
        work_item_relations = workitem_json.get("workItemRelations", [])

        # Display the work items to be added
        self.output_work_items(work_item_relations)
        
        # Skip API calls in dry run mode
        if dry_run:
            return

        # Create tree items in order of relations
        for order, relation in enumerate(work_item_relations):
            # Use source item as parent, or fall back to target_id if no source
            parent_id = (
                relation["source"]["id"]
                if relation.get("source")
                else target_id
            )

            self._azure_api_service.create_single_tree_item(
                project_id=project_id,
                child_id=relation["target"]["id"],
                parent_id=parent_id,
                order=order,
            )

    def output_work_items(self, work_item_relations):
        """
        Displays work items in a hierarchical tree format.

        Args:
            work_item_relations: List of work item relations to display
        """
        print("Work items to add:")
        level = 0
        work_items_with_level = {}
        
        for relation in work_item_relations:
            # Determine indentation level based on parent-child relationship
            if ("source" in relation and relation["source"] is not None):
                level = work_items_with_level[relation["source"]["id"]] + 1
            else:
                level = 0
            
            # Print work item with appropriate indentation
            print(f"{'  ' * level}- Work Item ID: {relation['target']['id']}")
            work_items_with_level[relation["target"]["id"]] = level

    def check_if_workitem_to_add_exist_on_tree(
        self,
        wi_tuple_id,
        list_wi_in_tree,
        list_of_children_id_to_delete
    ):
        """
        Validates that work items to add don't already exist in the tree.

        Args:
            wi_tuple_id: Work item IDs to migrate
            list_wi_in_tree: Existing work item IDs in the tree
            list_of_children_id_to_delete: Work items marked for deletion

        Raises:
            Exception: If a work item already exists and isn't marked for deletion
        """
        # Convert children IDs to strings for comparison
        list_of_children_id_to_delete = [
            str(child.get('id')) for child in list_of_children_id_to_delete
        ]
        
        # Check if any work item to add already exists in the tree
        for work_item_id in list_wi_in_tree:
            if (
                work_item_id in wi_tuple_id
                and work_item_id not in list_of_children_id_to_delete
            ):
                raise Exception(
                    f"Migration not possible: work item {work_item_id} already exists "
                    "in the tree and is not marked for deletion."
                )

    def window_by_children(
        self,
        work_items: List[Dict[str, Any]],
        target_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all children of a target work item.

        Args:
            work_items: List of all work items in the tree
            target_id: ID of the parent work item

        Returns:
            List of child work items (excluding the parent itself)

        Raises:
            ValueError: If parent work item is not found before its children
        """
        parent_id = None
        grouped_items = defaultdict(list)

        # Group items by their parent
        for item in work_items:
            if item.get("parent") == "-1":
                parent_id = str(item.get("id"))
                grouped_items[parent_id].append(item)
            else:
                if parent_id is None:
                    raise ValueError(
                        "Parent work item must be defined before its children."
                    )
                grouped_items[parent_id].append(item)

        # Return children only (exclude parent element at index 0)
        return grouped_items[target_id][1:]

    def normalize_wi_ids(self, value):
        try:
            if isinstance(value, str):
                value = ast.literal_eval(value)

            if isinstance(value, (list, tuple)):
                return tuple(int(v) for v in value)

            return (int(value),)

        except (ValueError, SyntaxError, TypeError) as e:
            raise ValueError(f"Invalid value for conversion: {value}") from e


    def get_tree_items_id(self,tree_items):
        if "value" in tree_items and 'count' in tree_items:
            return {str(item["id"]) for item in tree_items['value']}
        else:
            return {str(item["id"]) for item in tree_items}