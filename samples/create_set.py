# %% [markdown]
# # Create a Collection
#
# Create a vBase collection and confirm that it is available.
# %%

from utils import create_vbase_client_from_env, get_or_create_collection

COLLECTION_NAME = "Python Sample Collection"
COLLECTION_DESCRIPTION = "A collection created by the vBase Python samples."


# %% [markdown]
# ## Create and retrieve the collection
# %%
with create_vbase_client_from_env() as client:
    collection = get_or_create_collection(
        client,
        COLLECTION_NAME,
        COLLECTION_DESCRIPTION,
    )
    owner_address = client.get_current_user().last_address
    if not owner_address:
        raise RuntimeError("The current vBase account does not have an owner address.")

    matching_collection = next(
        (
            item
            for item in client.get_collections(user_address=owner_address)
            if item.cid.lower() == collection.cid.lower()
        ),
        None,
    )
    if matching_collection is None:
        raise RuntimeError("The collection could not be retrieved after creation.")

    print(f"Collection: {collection.name}")
    print(f"Collection CID: {collection.cid}")
    print(f"Owner address: {owner_address}")
    print("The collection is ready to receive stamps.")
