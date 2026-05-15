from app.db.database import SessionLocal, engine, Base
from app.models.models import User, Family, FamilyMember, Vacation
from datetime import date, timedelta
from app.services.vacation_service import VacationService

def seed():
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Create Demo User
    demo_user = User(email="demo@example.com", password="demo123")
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    # Create Family
    demo_family = Family(name="The Miller Family", owner_id=demo_user.id, default_country="CH")
    db.add(demo_family)
    db.commit()
    db.refresh(demo_family)
    
    # Create Family Members
    members_data = [
        {"name": "Alice (Mom)", "country": "CH", "subdivision": "ZH", "vacation_allowance": 25, "working_days": 5, "color": "#3b82f6"},
        {"name": "Bob (Dad)", "country": "MX", "vacation_allowance": 12, "working_days": 6, "color": "#10b981"},
        {"name": "Charlie (Kid)", "country": "DE", "vacation_allowance": 60, "working_days": 5, "color": "#f59e0b"},
        {"name": "Diana (Grandma)", "country": "US", "subdivision": "CA", "vacation_allowance": 365, "working_days": 0, "color": "#ec4899"},
    ]
    
    for member_info in members_data:
        member = FamilyMember(family_id=demo_family.id, **member_info)
        db.add(member)
        db.commit()
        db.refresh(member)
        
        # Add a sample vacation
        start = date(2026, 12, 23)
        end = date(2027, 1, 3)
        business_days = VacationService.calculate_business_days(
            start, end, member.country, member.subdivision, member.working_days
        )
        
        vac = Vacation(
            member_id=member.id,
            start_date=start,
            end_date=end,
            title="Christmas Break",
            business_days_spent=business_days
        )
        db.add(vac)
    
    db.commit()
    db.close()
    print("Database seeded with family data successfully!")

if __name__ == "__main__":
    seed()
