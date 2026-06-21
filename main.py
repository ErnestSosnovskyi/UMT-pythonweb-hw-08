from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contact Management API", version="1.0.0")

@app.post("/contacts", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db=db, contact=contact)

@app.get("/contacts", response_model=List[schemas.ContactResponse])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by first name, last name or email"),
    db: Session = Depends(get_db)
):
    return crud.get_contacts(db, skip=skip, limit=limit, search=search)

@app.get("/contacts/upcoming-birthdays", response_model=List[schemas.ContactResponse])
def read_upcoming_birthdays(db: Session = Depends(get_db)):
    return crud.get_upcoming_birthdays(db)

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = crud.update_contact(db, contact_id=contact_id, contact_data=contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    success = crud.delete_contact(db, contact_id=contact_id)
    if not success:
        raise HTTPException(status_code=204, detail="Contact not found")
    return None
