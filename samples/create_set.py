"""
This sample creates and validates a vBase set.
"""

import pprint

from vbase import VBaseClient


# Name for the test set to create.
SET_NAME = "TestDataset"


# Initialize vBase using environment variables.
vbc = VBaseClient.create_instance_from_env(".env")

# Create the set commitment.
receipt = vbc.add_named_set(SET_NAME)
print(f"add_named_set() receipt:\n{pprint.pformat(receipt)}")

# Validate the set commitment.
assert vbc.user_named_set_exists(vbc.get_default_user(), SET_NAME)
