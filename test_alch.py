from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    icon = Column(String)
    log_entries = relationship("LogEntry", back_populates="category", cascade="all, delete-orphan", passive_deletes=True)

class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    date = Column(Date)
    duration = Column(Integer)  # Duration in minutes
    notes = Column(String, nullable=True)

    category = relationship("Category", back_populates="log_entries")

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

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)