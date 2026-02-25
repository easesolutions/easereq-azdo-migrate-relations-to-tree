"""Service layer for Azure DevOps and Rado API interactions."""

import json
import requests
import urllib3
from uplink.auth import BasicAuth
from AzureApi.api import AzureApi, RadoApi
from AzureApi.Utilities.retry_request import retry_request
from configurations import TEST_ENV


class ApiService:
    """Handles all API communications with Azure DevOps and Rado."""

    # Disable SSL warnings for development (consider removing in production)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # HTTP session configuration
    _session = requests.Session()
    _session.verify = False

    # Azure DevOps API configuration
    __api_auth = BasicAuth('Basic', TEST_ENV.azure_auth_token)
    _azure_client = AzureApi(
        base_url=TEST_ENV.application_url,
        auth=__api_auth,
        client=_session
    )

    # Rado API configuration
    __rado_api_auth = BasicAuth(TEST_ENV.azure_auth_token, "")

    is_cloud = "dev.azure.com" in TEST_ENV.application_url
    url_prefix = "https://extmgmt." if is_cloud else "https://"
    _rado_api_url = f"{url_prefix}{TEST_ENV.application_url.split('//')[-1]}"
    _rado_client = RadoApi(
        _rado_api_url,
        auth=__rado_api_auth,
        client=_session
    )

    @retry_request
    def get_workitem_with_children_recursively(self, workitem_ids):
        """
        Retrieves a work item and all its child items recursively.

        Args:
            workitem_ids: Tuple, list, or string of work item IDs

        Returns:
            JSON response containing work item hierarchy from Azure DevOps API

        Raises:
            Exception: If the API request fails
        """
        # Build WIQL (Work Item Query Language) query for hierarchical retrieval
        query = (
            f"SELECT [System.Id] "
            f"FROM WorkItemLinks "
            f"WHERE ([Source].[System.Id] IN {workitem_ids}) "
            f"AND ([System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward') "
            f"MODE (Recursive)"
        )
        request_body = json.dumps({"query": query})

        # Execute the query against Azure DevOps API
        response = self._azure_client.get_workitem_hierachi(
            organization=TEST_ENV.azure_organization,
            request_body=request_body,
            api_version=TEST_ENV.api_version,
        )

        if response.ok:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve work items: {response.text}")

    @retry_request
    def create_single_tree_item(self, project_id, child_id, parent_id, order):
        """
        Creates a single item in the requirements tree.

        Args:
            project_id: Azure DevOps project ID
            child_id: ID of the child work item
            parent_id: ID of the parent work item
            order: Position/order in the tree

        Returns:
            ID of the created tree item

        Raises:
            Exception: If creation fails
        """
        # Build tree item structure
        tree_item = {
            "id": child_id,
            "parent": parent_id,
            "order": order
        }

        # Send creation request to Rado API
        response = self._rado_client.create_single_tree_item(
            project_id=project_id,
            body=tree_item
        )

        if response.status_code in (200, 201):
            return response.json().get("id")

        raise Exception(f"Failed to create tree item: {response.text}")

    @retry_request
    def get_all_tree_items(self, project_id):
        """
        Retrieves all tree items for a project.

        Args:
            project_id: Azure DevOps project ID

        Returns:
            List of tree items, or empty list if collection doesn't exist

        Raises:
            Exception: If retrieval fails with an unexpected error
        """
        response = self._rado_client.get_all_tree_items(project_id)

        if response.status_code == 200:
            return response.json()

        # Return empty list if collection doesn't exist (404 is not an error)
        if response.status_code == 404:
            print(f"Collection does not exist (404) for project '{project_id}'.")
            return []

        raise Exception(f"Failed to retrieve tree items: {response.text}")

    @retry_request
    def delete_tree_item(self, project_id, tree_item_list, dry_run: bool) -> bool:
        """
        Recursively deletes work items from the requirements tree.

        Args:
            project_id: Azure DevOps project ID
            tree_item_list: List of tree items to delete
            dry_run: If True, only logs the items without deleting

        Returns:
            True if deletion was successful or skipped (dry run)

        Raises:
            Exception: If deletion fails
        """
        # Base case: no more items to delete
        if not tree_item_list:
            return True

        current_item = tree_item_list[0]
        item_id = current_item.get("id")

        # Recursively delete remaining items first
        self.delete_tree_item(project_id, tree_item_list[1:], dry_run)

        # In dry run mode, log deletion without actually deleting
        if dry_run:
            print(f"Dry run: would remove item {item_id} from tree.")
            return True

        # Delete current item from Rado API
        print(f"Removing item {item_id} from tree...")
        response = self._rado_client.delete_single_tree_item(
            project_id=project_id,
            item_id=item_id
        )

        if response.status_code not in (200, 204):
            raise Exception(f"Failed to delete item {item_id}: {response.text}")

        return True

    @retry_request
    def get_project_id(self, project_name):
        """
        Retrieves the project ID by project name.

        Args:
            project_name: Name of the Azure DevOps project

        Returns:
            Project ID string

        Raises:
            HTTPError: If the project is not found or request fails
        """
        # Query Azure DevOps for project details
        project_response = self._azure_client.get_project_by_id_or_name(
            organization=TEST_ENV.azure_organization,
            project_id_or_name=project_name,
            api_version=TEST_ENV.api_version,
        )

        if project_response.status_code == 200:
            return project_response.json().get("id")

        # Raise HTTP error if request was unsuccessful
        project_response.raise_for_status()

