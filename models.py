import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Shots(Base):
    __tablename__ = 'shots'

    enums=('1W', '3W', '4', '5', '6', '7', '8', '9', 'P', '52', '56')

    id = db.Column(db.Integer, primary_key=True)
    club = db.Column(db.Enum(*enums))
    total_distance = db.Column(db.Integer)
    carry_distance = db.Column(db.Integer)
    missed = db.Column(db.Boolean)
    date = db.Column(db.Date)


# Base.metadata.create_all(engine)

# df = pd.read_sql_table(
#     'shots',
#     engine,
#     index_col='id',
#     parse_dates=['date'])