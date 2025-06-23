"""vBase File Stamper CLI"""
import argparse
from pathlib import Path
from dotenv import load_dotenv
import os

from core import LocalFileFolderDataSource, VBaseProcessingPipeline, VBaseClient

load_dotenv()

def run_pipeline(api_url: str, users_folder: Path, run: bool, log_file: Path = None):
    """Run the stamping pipeline for all users in the specified folder."""
    if not users_folder.exists():
        raise ValueError(f"Folder does not exist: {users_folder}")

    data_source = LocalFileFolderDataSource(users_folder)
    users_config = data_source.load_users()

    for user_id, user_info in users_config["users"].items():
        print(f"\n=== Processing user: {user_id} ===")

        api_key = user_info.get("api_key")
        if not api_key:
            print(f"Skipping user {user_id}, missing API key.")
            continue

        stamping_client = VBaseClient(base_url=api_url, api_token=api_key)
        pipeline = VBaseProcessingPipeline(data_source, stamping_client)

        if run:
            pipeline.run(current_user=user_id)
            pipeline.print_summary()
            if log_file:
                pipeline.write_log(log_file)
                print(f"\nLog written to: {log_file}")
        else:
            preview = pipeline.preview(current_user=user_id)
            print("\n=== Preview Mode (use --run to execute stamping) ===")
            for entry in preview:
                print(f"{entry['file']} -> Collection: {entry['collection']} | User: {entry['user']}")

def main():
    """Main function to parse arguments and run the stamping pipeline.
    python stamp_cli.py --users-folder ./samples
    """
    parser = argparse.ArgumentParser(description="vBase File Stamper CLI")
    parser.add_argument("--users-folder", type=str, required=True, help="Path to /users/ folder")
    parser.add_argument("--run", action="store_true", help="Run stamping. If not set, shows preview only.")
    parser.add_argument("--log-file", type=str, help="Optional path to write log of stamped files (JSON)")
    args = parser.parse_args()

    users_folder = Path(args.users_folder).resolve()
    if not users_folder.exists():
        raise ValueError(f"Folder does not exist: {users_folder}")

    api_url = os.getenv("VBASE_API_URL")
    if not api_url:
        raise EnvironmentError("Missing VBASE_API_URL in environment variables")

    preview_run = args.run
    run_pipeline(api_url, users_folder, preview_run)


if __name__ == "__main__":
    """Run the CLI tool."""
    main()