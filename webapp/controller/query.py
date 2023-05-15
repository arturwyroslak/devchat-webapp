"""
query.py contains functions to query the database.
"""
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from webapp.model import Organization, User, organization_user
from webapp.model import AccessKey


def get_users_of_organization(db: Session, organization_id: int,
                              columns: List[str] = None) -> List[list]:
    """
    Get all users of an organization.

    Args:
        organization_id (int): Unique ID of the organization
        columns (list, optional): List of columns to return. Default is ['id', 'username', 'email'].

    Returns:
        list: List of lists containing user information.
            Each inner list contains user data in the same order as the input or default columns.
    """
    if columns is None:
        columns = ['id', 'username', 'email']

    users = db.query(User).with_entities(*[getattr(User, column) for column in columns]). \
        join(organization_user). \
        join(Organization). \
        filter(Organization.id == organization_id).all()
    return [list(user) for user in users]


def get_valid_keys_of_organization(db: Session, organization_id: int) -> List[AccessKey]:
    """
    Get all valid access keys' information of an organization.

    Args:
        organization_id (int): Unique ID of the organization

    Returns:
        list: List of AccessKey objects containing valid keys' information.
    """
    return db.query(AccessKey).join(Organization).filter(
        Organization.id == organization_id,
        AccessKey.revoke_time == None).all()  # pylint: disable=C0121


def get_revoked_key_hashes(db: Session, start_time: datetime, end_time: datetime) -> List[str]:
    """
    Get revoked access keys that were revoked within the specified time range [start_time, end_time).

    Args:
        start_time (datetime): Start time of the time range
        end_time (datetime): End time of the time range

    Returns:
        list: List of key hashes of revoked keys within the specified time range.
    """
    revoked_keys = db.query(AccessKey.key_hash). \
        filter(AccessKey.revoke_time >= start_time, AccessKey.revoke_time < end_time).all()
    return [key_hash[0] for key_hash in revoked_keys]