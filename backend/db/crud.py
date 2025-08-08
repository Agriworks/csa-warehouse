from uuid import UUID
from db.models import User, Dataset
from db.database import users_collection, datasets_collection


def user_to_dict(user: User):
    user_dict = user.model_dump()
    user_dict["_id"] = str(user_dict.pop("id"))
    return user_dict


def dataset_to_dict(dataset: Dataset):
    ds_dict = dataset.model_dump()
    ds_dict["_id"] = str(ds_dict.pop("id"))
    ds_dict["uploader"] = user_to_dict(ds_dict["uploader"])
    ds_dict["uploadDate"] = ds_dict["uploadDate"].isoformat()
    return ds_dict


# User Operations
def create_user(user: User):
    users_collection.insert_one(user_to_dict(user))


def get_user(user_id: UUID):
    result = users_collection.find_one({"_id": str(user_id)})
    return result


def update_user(user_id: UUID, user_data: dict):
    result = users_collection.update_one({"_id": str(user_id)}, {"$set": user_data})
    return result.modified_count


def delete_user(user_id: UUID):
    result = users_collection.delete_one({"_id": str(user_id)})
    return result.deleted_count


# Dataset Operations
def create_dataset(dataset: Dataset):
    datasets_collection.insert_one(dataset_to_dict(dataset))


def get_dataset(dataset_id: UUID):
    result = datasets_collection.find_one({"_id": str(dataset_id)})
    return result


def delete_dataset(dataset_id: UUID):
    result = datasets_collection.delete_one({"_id": str(dataset_id)})
    return result.deleted_count
