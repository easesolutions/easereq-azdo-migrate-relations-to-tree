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
* One **Environment Variable** with the name of configuration that will be used to migrate 
* An **API Token** (Personal Access Token) with permissions to modify the requirements tree

---


###  Configuration File

To connect this project with your Azure DevOps environment, you must create a configuration file with the required credentials and settings.

#### File Requirements

- **Filename:** `config.yaml`  
- **Location:** Root directory of the project  
- **Prerequisite:** Ensure the **easeRequirements** extension is installed in your target Azure DevOps environment before running the migration.

---

###  Example `config.yaml`

```yaml
settings:
  env:
    application_url: <Your Azure DevOps URL (e.g. https://dev.azure.com/)>
    azure_organization: <Your organization name>
    api_version: <Azure API version (e.g. 7.1-preview.1)>
    azure_pat: <Your Personal Access Token>
    extension_name: <Extension name (e.g. requirements)>
    
  development:
    application_url: <Your secondary Azure DevOps URL>
    azure_organization: <Your organization name>
    api_version: <Azure API version for this environment>
    azure_pat: <Your Personal Access Token>
    extension_name: <Extension name (e.g. azure-requirements)>
```

---

###  Configuration Details

| Setting              | Description                                        | Example                    |
| -------------------- | -------------------------------------------------- | -------------------------- |
| `application_url`    | Base URL of your Azure DevOps instance             | `https://dev.azure.com/`   |
| `azure_organization` | Azure DevOps organization name                     | `my-organization`          |
| `api_version`        | Azure DevOps REST API version                      | `7.1-preview.1`, `7.2`     |
| `azure_pat`          | Personal Access Token used for authentication      | *(see instructions below)* |
| `extension_name`     | Name of the installed extension in the environment | `requirements`             |

---

###  Useful Resources

* Azure DevOps API version reference:
  [https://learn.microsoft.com/en-us/rest/api/azure/devops/#api-and-tfs-version-mapping](https://learn.microsoft.com/en-us/rest/api/azure/devops/#api-and-tfs-version-mapping)

---

###  Generating a Personal Access Token (PAT)

1. Visit:
   [https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)

2. Create a new token with the following scopes:

   * **Work Items** → Read
   * **Extension Data** → Read & Write

---

### Setting the Environment Variable

The application uses an environment variable named `APP_ENV` to determine which configuration to load. If no environment variable is configured, the tool will use the default configuration.

#### On Linux / macOS

```bash
export APP_ENV=production
```

#### On Windows (Command Prompt)

```cmd
set APP_ENV=production
```

#### On Windows (PowerShell)

```powershell
$env:APP_ENV="production"
```

---

### Example

If `APP_ENV=development`, the application will load the `development` configuration block from `config.yaml`.

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
