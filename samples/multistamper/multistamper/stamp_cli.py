"""vBase File Stamper CLI"""
import argparse
from pathlib import Path
from dotenv import load_dotenv
import os
import json

from .core import LocalDataSource, Pipeline, ApiClient
load_dotenv()

def run_pipeline(api_url: str, users_folder: Path, run: bool, log_file: Path = None):
    """Run the stamping pipeline for all users in the specified folder."""
    if not users_folder.exists():
        raise ValueError(f"Folder does not exist: {users_folder}")

    data_source = LocalDataSource(users_folder)
    users_config = data_source.load_users()
    if not users_config["users"]:
        raise ValueError("No users found in the specified folder.")

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


def setup():
    """Setup wizard for multistamper configuration."""
    print("Welcome to the multistamper setup wizard!\n")

    # 1. Root folder setup
    root_folder = Path(input("Enter root folder name (e.g., samples): ").strip()).resolve()
    if root_folder.exists():
        print(f"📁 Root folder '{root_folder}' already exists. Using it.")
    else:
        root_folder.mkdir(parents=True)
        print(f"✅ Created root folder: {root_folder}")

    # Main user loop
    while True:
        print("\n👤 Setting up new user")
        user_name = input("Enter user Name: ").strip()
        user_folder = root_folder / user_name

        if user_folder.exists():
            print(f"⚠️  User folder '{user_name}' already exists. Skipping user setup.")
        else:
            user_folder.mkdir(parents=True)
            print(f"✅ Created user folder: {user_folder}")

            # 2. API Key setup → .env
            api_key = input("Enter API Key for this user: ").strip()
            env_path = user_folder / ".env"
            with open(env_path, "w") as f:
                f.write(f"API_KEY={api_key}\n")
            print(f"✅ Saved .env file: {env_path}")

        # 3. Collections setup
        collections_folder = user_folder / "collections"
        collections_folder.mkdir(parents=True, exist_ok=True)

        while True:
            print("\n📦  Setup new collection for this user")
            collection_name = input("  - Enter collection name (folder name): ").strip()
            collection_cid = input("  - Enter collection CID: ").strip()

            collection_path = collections_folder / collection_name
            config_path = collection_path / "collection_config.json"

            if collection_path.exists():
                print(f"⚠️  Collection folder '{collection_name}' already exists. Skipping.")
            else:
                collection_path.mkdir(parents=True)
                collection_config = {
                    "collection_name": collection_name,
                    "collection_cid": collection_cid
                }
                with open(config_path, "w") as f:
                    json.dump(collection_config, f, indent=2)
                print(f"✅ Created collection '{collection_name}' with config: {config_path}")

            another_collection = input("  - Add another collection for this user? [y/N]: ").strip().lower()
            if another_collection != 'y':
                break

        another_user = input("\n➕ Add another user? [y/N]: ").strip().lower()
        if another_user != 'y':
            break

    print(f"\n✅ Setup completed! Root: {root_folder}")                

def main():
    parser = argparse.ArgumentParser(description="vBase File Stamper CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--setup", action="store_true", help="Run setup wizard")
    group.add_argument("--users-folder", type=str, help="Path to users folder for stamping")
    parser.add_argument("--log-file", type=str, help="Optional path to write log of stamped files")

    args = parser.parse_args()

    if args.setup:
        setup()
    else:
        users_folder = Path(args.users_folder).resolve()
        if not users_folder.exists():
            raise ValueError(f"Folder does not exist: {users_folder}")

        api_url = os.getenv("VBASE_API_URL")
        if not api_url:
            raise EnvironmentError("Missing VBASE_API_URL in environment variables")

        print(f"Configuration file: {json.dumps(users_folder, indent=2, default=str)}")

        # Step 1: Preview first
        run_pipeline(api_url, users_folder, run=False)

        # Step 2: Ask user for confirmation
        user_input = input("\nDo you want to stamp these files? (y/N): ").strip().lower()
        if user_input == "y":
            run_pipeline(api_url, users_folder, run=True, log_file=Path(args.log_file) if args.log_file else None)
        else:
            print("Operation cancelled.")


if __name__ == "__main__":
    """Run the CLI tool."""
    main()