# Migration by Inheritance to the Requirements Tree

## DISCLAIMER

This repository and the accompanying code are provided on an "AS-IS" and "AS-AVAILABLE" basis, without any warranties or guarantees of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement. 

Ease Solutions assumes no responsibility or liability for any direct, indirect, incidental, or consequential damages, including but not limited to data loss, financial loss, or business interruption, arising from the use of this repository or its contents. 

Users are solely responsible for testing and validating the migration process in a controlled test environment prior to applying it in a production environment. By using the code on this repository, you acknowledge and agree to these terms.


## Prerequisites

* Python **3.14.0**
* Project dependencies installed:

  ```bash
  pip install -r requirements.txt
  ```

## Setup

### Requirements

* One **Azure DevOps** instance with **easeRequirements** extension installed
* A properly configured `config.yaml` file for the target instance
* An **API Token** (Personal Access Token) with permissions to modify the requirements tree

### Configuration File

Create a configuration file containing the information required to access your Azure DevOps environment.

* **Filename:** `config.yaml`
* **Location:** Place in the project root directory
* **Important:** Ensure the **easeRequirements** extension is already installed in your target Azure DevOps environment before running the migration

#### Example `config.yaml`

```yaml
settings:
  env:
    application_url: <Your AzDO URL (e.g.: https://dev.azure.com/)>
    azure_organization: <Your organization name>
    api_version: <Azure API Version (e.g.: 7.1-preview)>
    azure_pat: <Your Personal Access Token>
```

#### Configuration Details

| Setting | Description | Example |
|---------|-------------|---------|
| `application_url` | Base URL of your Azure DevOps instance | `https://dev.azure.com/` |
| `azure_organization` | Organization name in Azure DevOps | `my-organization` |
| `api_version` | Azure DevOps API version | `7.0` or `7.1` |
| `azure_pat` | Personal Access Token for authentication | (see PAT generation below) |

**For the correct Azure API Version:** https://learn.microsoft.com/en-us/rest/api/azure/devops/#api-and-tfs-version-mapping

**To generate a Personal Access Token:**
1. Visit: https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate
2. Required scopes:
   * Work items - Read
   * Extension Data - Read & Write

---

## Running the Migration Script

Execute the migration using the Python script `run_migration.py`:

```bash
python .\run_migration.py "(8402)" "Project Automation Basic" -1
# or with dry run enabled
python .\run_migration.py "(8402)" "Project Automation Basic" -1 true
```

This script requires **three command-line arguments** (the fourth is optional).

---

## Command-Line Arguments

### Argument 1: Work Item IDs

A **tuple** of work item IDs to migrate. Must be enclosed in quotation marks and parentheses.

**Format:** `"(id1, id2, id3)"` or `"(id1)"`

**Examples:**

```bash
"(8569, 9456, 1234)"
"(1234)"
```

---

### Argument 2: Project Name or ID

The Azure DevOps project name or project ID where the work items are located.

**Note:** If the project name contains spaces, enclose it in quotation marks.

**Examples:**

```bash
"My Project Name"
MyProjectName
```

---

### Argument 3: Target Work Item ID

Specifies where the migrated work items will be placed in the requirements tree.

| Value | Behavior |
|-------|----------|
| `-1` | Migrate work items to the **root** of the requirements tree |
| `<work_item_id>` | Add migrated work items as **children** of the specified work item |

**Examples:**

```bash
-1
8756
```

---

### Argument 4: Dry Run Flag (Optional)

Controls whether changes are applied to the live environment.

**Default value:** `false`

| Value | Behavior |
|-------|----------|
| `true` | Simulates the migration without making changes; logs full execution flow for debugging |
| `false` | **Applies changes** - work items may be removed or added; the requirements tree will be modified |

---

## Example Commands

### Dry run the migration of a single work item to root

```bash
python .\run_migration.py "(8402)" "Project Automation Basic" -1 True
```

### Migrate multiple work items as children of work item 8756 (apply changes)

```bash
python .\run_migration.py "(8402, 8403, 8404)" "Project Automation Basic" 8756 False
```

### Migrate a single work item to root (apply changes)

```bash
python .\run_migration.py "(8402)" "Project Automation Basic" -1
```

---

## Troubleshooting

* **Authentication errors (401):** Verify your Personal Access Token is valid and has the required scopes
* **Not found errors (404):** Check that the project name/ID and work item IDs are correct
* **Extension not installed:** Ensure the **easeRequirements** extension is installed in your Azure DevOps environment
* **Dry run first:** Always test with dry run mode enabled (`true`) before applying changes to production
