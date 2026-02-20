"""Entry point for running work item migration from Azure DevOps to Rado."""

import sys
import re
from migration.migrate_ado_wi_to_rado import Migration


if __name__ == '__main__':

    # Check if minimum required arguments are provided
    if len(sys.argv) >= 3:
        print("Running migration with:")
        wi_id_tuple = sys.argv[1]
        project_name = sys.argv[2]
        target = sys.argv[3]        

        # Convert single number to tuple format for consistency
        if bool(re.match(r'^\d+$', wi_id_tuple)):
            wi_id_tuple = "(" + wi_id_tuple + ")"

        # Validate tuple format: (1) or (1,2,3)
        tuple_pattern = r'^\(\s*\d+(?:\s*,\s*\d+)*\s*\)$'
        if bool(re.match(tuple_pattern, wi_id_tuple)):
            try:
                # Parse optional dry_run argument
                dry_run = sys.argv[4]
                if dry_run.lower() == "true":
                    dry_run = True
                elif dry_run.lower() == "false":
                    dry_run = False
                else:
                    raise Exception("Invalid argument for dry_run")
            except Exception:
                # If the argument is not provided or invalid, default to False
                dry_run = False

            # Display migration parameters
            print(f"* Work item IDs: {wi_id_tuple}")
            print(f"* Project name:  {project_name}")
            print(f"* Target WI ID:  {target}")
            print(f"* Dry run:       {dry_run}")

            # Execute migration
            migration_obj = Migration()
            migration_obj.start_migration(wi_id_tuple, project_name, target, dry_run)
        else:
            raise Exception(
                "Invalid argument for work items to be migrated: "
                "the value must be a tuple. example: (value,value)"
            )
    else:
        print(
            "No arguments provided. "
            "Usage: python run_migration.py (<work item ids>) <project name> <target work item id> <optional: dry run>"
        )