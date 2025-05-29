from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, UTC

Base = declarative_base()

class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    veiculo = Column(String(255), index=True)
    marca = Column(String(255), index=True)
    ano = Column(Integer, index=True)
    descricao = Column(String(255), nullable=True)
    vendido = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.now(UTC))
    updated = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
