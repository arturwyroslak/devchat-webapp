"""
query.py contains functions to query the database.
"""
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from webapp.model import Organization, User, organization_user
from webapp.model import AccessKey


def get_organization_id_by_name(db: Session, org_name: str) -> int:
    """
    Get the organization ID with the given name.

    Args:
        org_name (str): Name of the organization

    Returns:
        int: the organization ID with the given name
    """
    org_id = db.query(Organization.id).filter(Organization.name == org_name).first()
    if org_id is None:
        return None
    return org_id[0]


def get_users_of_organization(db: Session, organization_id: int,
                              columns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get all users of an organization.

    Args:
        organization_id (int): Unique ID of the organization
        columns (list, optional): List of columns to return. Default is ['id', 'username', 'email'].

    Returns:
        list: List of dictionaries containing user information.
            Each dictionary contains user data with keys matching the input or default columns.
    """
    if columns is None:
        columns = ['id', 'username', 'email']

    users = db.query(User).with_entities(*[getattr(User, column).label(column) for column in columns]). \
        join(organization_user). \
        join(Organization). \
        filter(Organization.id == organization_id).all()

    return [row._asdict() for row in users]


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
    Get access keys that were revoked within the specified time range [start_time, end_time).

    Args:
        start_time (datetime): Start time of the time range
        end_time (datetime): End time of the time range

    Returns:
        list: List of key hashes of revoked keys within the specified time range.
    """
    revoked_keys = db.query(AccessKey.key_hash). \
        filter(AccessKey.revoke_time >= start_time, AccessKey.revoke_time < end_time).all()
    return [key_hash[0] for key_hash in revoked_keys]
