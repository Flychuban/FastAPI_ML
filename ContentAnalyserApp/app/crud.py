from sqlalchemy.orm import Session
import models, schemas

def create_search_term(db: Session, term: str) -> str:
    db_search_term = models.SearchTerm(term=term)