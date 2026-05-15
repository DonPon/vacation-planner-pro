from sqlalchemy.orm import Session
from app.models.models import FamilyMember, Family

def get_family_members(db: Session, user_id: int):
    if not user_id: return []
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    if not family: return []
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
    for m in members:
        spent = sum(v.business_days_spent for v in m.vacations)
        m.remaining_balance = m.vacation_allowance - spent
    return members
