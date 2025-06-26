"""vBase File Stamper CLI"""
import argparse
from pathlib import Path
from dotenv import load_dotenv
import os

from core import LocalDataSource, Pipeline, ApiClient

load_dotenv()

def run_pipeline(api_url: str, users_folder: Path, run: bool, log_file: Path = None):
    """Run the stamping pipeline for all users in the specified folder."""
    if not users_folder.exists():
        raise ValueError(f"Folder does not exist: {users_folder}")

    data_source = LocalDataSource(users_folder)
    users_config = data_source.load_users()

    for user_id, user_info in users_config["users"].items():
        print(f"\n=== Processing user: {user_id} ===")

        api_key = user_info.get("api_key")
        if not api_key:
            print(f"Skipping user {user_id}, missing API key.")
            continue

        stamping_client = ApiClient(base_url=api_url, api_token=api_key)
        pipeline = Pipeline(data_source, stamping_client)

        if run:
            pipeline.run(current_user=user_id)
            pipeline.print_summary()
            if log_file:
                pipeline.write_log(log_file)
                print(f"\nLog written to: {log_file}")
        else:
            preview = pipeline.preview(current_user=user_id)
            print("\n=== Preview Mode  ===")
            print(f"User: {user_id}")
            for entry in preview:
                print(f"File: {entry['file']}")
                print(f"Sub folder: {entry['collection']}")
                print(f"CID: {entry['collection_cid']}")
                print(f"Path: {entry['path']}")
                print("-" * 50)  # separator line
                

def main():
    """Main function to parse arguments and run the stamping pipeline."""
    parser = argparse.ArgumentParser(description="vBase File Stamper CLI")
    parser.add_argument("--users-folder", type=str, required=True, help="Path to /users/ folder")
    parser.add_argument("--log-file", type=str, help="Optional path to write log of stamped files (JSON)")
    args = parser.parse_args()

    users_folder = Path(args.users_folder).resolve()
    if not users_folder.exists():
        raise ValueError(f"Folder does not exist: {users_folder}")

    api_url = os.getenv("VBASE_API_URL")
    if not api_url:
        raise EnvironmentError("Missing VBASE_API_URL in environment variables")

    # Step 1: Preview first
    run_pipeline(api_url, users_folder, run=False)

    # Step 2: Ask user for confirmation
    user_input = input("\nDo you want to apply these changes? (y/N): ").strip().lower()
    if user_input == "y":
        run_pipeline(api_url, users_folder, run=True, log_file=Path(args.log_file) if args.log_file else None)
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    """Run the CLI tool."""
    main()