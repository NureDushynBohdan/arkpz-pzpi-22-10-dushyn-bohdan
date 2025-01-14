from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime, Float, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.sql import func

Base = declarative_base()

class Technician(Base):
    __tablename__ = 'Technician'
    
    TechnicianID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    Specialization = Column(String(100), nullable=False)
    Availability = Column(String(50))
    
    aquariums = relationship('Aquarium', back_populates='technician')


class Client(Base):
    __tablename__ = 'Client'
    
    ClientID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    
    aquariums = relationship('Aquarium', back_populates='client')


class Aquarium(Base):
    __tablename__ = 'Aquarium'
    
    AquariumID = Column(Integer, primary_key=True, autoincrement=True)
    Location = Column(String(255), nullable=False)
    FishTypes = Column(Text, nullable=False)
    WaterParameters = Column(Text, nullable=False)
    TechnicianID = Column(Integer, ForeignKey('Technician.TechnicianID'))
    ClientID = Column(Integer, ForeignKey('Client.ClientID'))
    
    technician = relationship('Technician', back_populates='aquariums')
    client = relationship('Client', back_populates='aquariums')
    
    sensors = relationship('IoTSensor', back_populates='aquarium')


class IoTSensor(Base):
    __tablename__ = 'IoT_Sensor'

    SensorID = Column(Integer, primary_key=True, autoincrement=True)
    Type = Column(Enum('Temperature', 'pH', 'Other', name='sensor_type'), nullable=False)
    Value = Column(String(50), nullable=False)
    AquariumID = Column(Integer, ForeignKey('Aquarium.AquariumID'), nullable=False)

    aquarium = relationship('Aquarium', back_populates='sensors')
    data = relationship("SensorDataInDB", back_populates="sensor") 

class Administrator(Base):
    __tablename__ = 'Administrator'
    
    AdminID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    Role = Column(String(50), nullable=False)

class SystemLog(Base):
    __tablename__ = "system_logs"
    LogID = Column(Integer, primary_key=True, index=True)
    Operation = Column(String(255), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    UserID = Column(Integer, nullable=False)
    Details = Column(String(255), nullable=True)

class SensorData(BaseModel):
    temperature: float
    humidity: float
    sensor_id: int 

    class Config:
        from_attributes = True

class SensorDataResponse(BaseModel):
    id: int
    temperature: float
    humidity: float
    sensor_id: int  

    class Config:
        from_attributes = True 

class SensorDataInDB(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())
    sensor_id = Column(Integer, ForeignKey("IoT_Sensor.SensorID")) 

    sensor = relationship("IoTSensor", back_populates="data") 

class SensorTrendReport(BaseModel):
    sensor_id: int  
    coefficient: float 
    trend_description: str

    class Config:
        from_attributes = True
