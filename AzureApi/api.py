"""API client definitions for Azure DevOps and Rado API interactions."""

from uplink import post, Body, Consumer, headers, json, put, get, delete
from configurations import TEST_ENV


class AzureApi(Consumer):
    """API client for Azure DevOps work item queries."""

    @headers({"Content-Type": "application/json"})
    @post("{organization}/_apis/wit/wiql?api-version={api_version}")
    def get_workitem_hierachi(self, organization: str, request_body: Body, api_version: str):
        """
        Executes a Work Item Query Language (WIQL) query against Azure DevOps.

        Args:
            organization: Azure DevOps organization name
            request_body: JSON body containing the WIQL query
            api_version: API version to use (e.g., '7.0')

        Returns:
            Response object containing work item relations and hierarchy
        """


    @headers({"Accept": "application/json"})
    @get("{organization}/_apis/projects/{project_id_or_name}?api-version={api_version}")
    def get_project_by_id_or_name(self, organization: str, project_id_or_name: str, api_version: str):
        """
        Retrieves project details from Azure DevOps using either project ID or name.

        Args:
            organization: Azure DevOps organization name
            project_id_or_name: Project ID or name to search for
            api_version: API version to use (e.g., '7.0')
        Returns:
            Response object containing project details if found, or error if not found
        """

class RadoApi(Consumer):
    """API client for Rado requirements tree management."""

    API_VERSION = TEST_ENV.api_version
    url_tree_items = (
        f"{TEST_ENV.azure_organization}/_apis/ExtensionManagement/InstalledExtensions/"
        f"easesol/{TEST_ENV.extension_name}/Data/Scopes/Default/Current/Collections/TreeItems_"
    )

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @headers({"Content-Type": "application/json"})
    @json
    @put("{}{}".format(url_tree_items, "{project_id}/Documents/"))
    def create_single_tree_item(self, project_id, body: Body):
        """
        Creates a single tree item in the Rado requirements tree.

        Args:
            project_id: Azure DevOps project ID
            body: JSON body containing tree item data (id, parent, order)

        Returns:
            Response object with the created tree item details
        """

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @get("{}{}".format(url_tree_items, "{project_id}/Documents/"))
    def get_all_tree_items(self, project_id):
        """
        Retrieves all tree items for a given project.

        Args:
            project_id: Azure DevOps project ID

        Returns:
            Response object containing list of all tree items
        """

    @headers({"Accept": f"application/json; api-version={API_VERSION}"})
    @delete("{}{}".format(url_tree_items, "{project_id}/Documents/{item_id}"))
    def delete_single_tree_item(self, project_id, item_id):
        """
        Deletes a single tree item from the Rado requirements tree.

        Args:
            project_id: Azure DevOps project ID
            item_id: ID of the tree item to delete

        Returns:
            Response object indicating success or failure of deletion
        """

