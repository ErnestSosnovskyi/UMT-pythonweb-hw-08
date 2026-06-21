from sqlalchemy.orm import Session
from sqlalchemy import or_, extract
from datetime import date, timedelta
from typing import Optional
import models, schemas

def get_contacts(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None):
    query = db.query(models.Contact)
    if search:
        query = query.filter(
            or_(
                models.Contact.first_name.ilike(f"%{search}%"),
                models.Contact.last_name.ilike(f"%{search}%"),
                models.Contact.email.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, contact_id: int, contact_data: schemas.ContactUpdate):
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return None
    for key, value in contact_data.model_dump(exclude_unset=True).items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return True
    return False

def get_upcoming_birthdays(db: Session):
    today = date.today()
    upcoming_contacts = []

    all_contacts = db.query(models.Contact).all()
    for contact in all_contacts:
        try:
            bday_this_year = contact.birthday.replace(year=today.year)
        except ValueError:
            bday_this_year = contact.birthday.replace(year=today.year, day=28)
        
        if bday_this_year < today:
            bday_this_year = bday_this_year.replace(year=today.year + 1)
        
        if today <= bday_this_year <= today + timedelta(days=7):
            upcoming_contacts.append(contact)
    return upcoming_contacts