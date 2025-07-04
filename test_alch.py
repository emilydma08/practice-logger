from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement = True)
    name = Column(String)
    description = Column(String)
    icon = Column(String)

engine = create_engine('sqlite:///pl.db', echo=True)


SessionLocal = sessionmaker(bind=engine)
# session = Session()

# new_category = Category(
#     name="Art",
#     description="Creative and visual expressions",
#     icon="🎨"
# )

# session.add(new_category)
# session.commit()

# categories = session.query(Category).all()
# for c in categories:
#     print(c.name, c.description, c.icon)


# session.close()