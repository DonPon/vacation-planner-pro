from datetime import date

from sqlalchemy.orm import Session

from app.models.models import FamilyMember, Family
from app.services.vacation_service import VacationService


def vacation_days_in_year(vacation, member, year):
    """Business days of a trip that fall within the given calendar year."""
    if not vacation.start_date or not vacation.end_date:
        return 0

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    start = max(vacation.start_date, year_start)
    end = min(vacation.end_date, year_end)
    if start > end:
        return 0

    return VacationService.calculate_business_days(
        start,
        end,
        member.country,
        member.subdivision,
        member.working_days if member.working_days is not None else 5,
    )


def get_family_members(db: Session, user_id: int, year: int = None):
    if not user_id:
        return []
    family = db.query(Family).filter(Family.owner_id == user_id).first()
    if not family:
        return []
    year = year or family.default_year or date.today().year
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
    for m in members:
        m.spent_days_in_year = sum(
            vacation_days_in_year(vacation, m, year) for vacation in m.vacations
        )
        m.remaining_balance = m.vacation_allowance - m.spent_days_in_year
    return members
