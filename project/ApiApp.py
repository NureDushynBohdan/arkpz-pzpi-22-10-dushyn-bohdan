from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Technician, Client, Aquarium, IoTSensor, Administrator, SensorDataResponse, SensorDataInDB, SensorData, SystemLog, SensorTrendReport
from fastapi import HTTPException
from sklearn.linear_model import LinearRegression
import numpy as np
from typing import Dict

DATABASE_URL = "mysql+pymysql://root:@localhost/AquariumSystem" 
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/technicians/")
def create_technician(name: str, specialization: str, availability: str, db: Session = Depends(get_db)):
    db_technician = Technician(Name=name, Specialization=specialization, Availability=availability)
    db.add(db_technician)
    db.commit()
    db.refresh(db_technician)
    return db_technician

@app.get("/technicians/")
def get_technicians(db: Session = Depends(get_db)):
    technicians = db.query(Technician).all()
    return technicians

@app.post("/aquariums/")
def create_aquarium(location: str, fish_types: str, water_parameters: str, technician_id: int, client_id: int, db: Session = Depends(get_db)):
    db_aquarium = Aquarium(Location=location, FishTypes=fish_types, WaterParameters=water_parameters, TechnicianID=technician_id, ClientID=client_id)
    db.add(db_aquarium)
    db.commit()
    db.refresh(db_aquarium)
    return db_aquarium

@app.get("/aquariums/")
def get_aquariums(db: Session = Depends(get_db)):
    aquariums = db.query(Aquarium).all()
    return aquariums

@app.post("/sensors/")
def create_sensor(sensor_type: str, value: str, aquarium_id: int, db: Session = Depends(get_db)):
    db_sensor = IoTSensor(Type=sensor_type, Value=value, AquariumID=aquarium_id)
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@app.get("/sensors/", response_model=List[dict])
def get_all_iot_sensors(db: Session = Depends(get_db)):
    sensors = db.query(IoTSensor).all()
    if not sensors:
        raise HTTPException(status_code=404, detail="No IoT sensors found")
    return [{"sensor_id": sensor.SensorID, "type": sensor.Type, "value": sensor.Value, "aquarium_id": sensor.AquariumID} for sensor in sensors]


@app.delete("/technicians/{technician_id}/")
def delete_technician(technician_id: int, db: Session = Depends(get_db)):
    technician = db.query(Technician).filter(Technician.TechnicianID == technician_id).first()
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")
    db.delete(technician)
    db.commit()
    return {"message": "Technician deleted successfully"}

@app.delete("/aquariums/{aquarium_id}/")
def delete_aquarium(aquarium_id: int, db: Session = Depends(get_db)):
    aquarium = db.query(Aquarium).filter(Aquarium.AquariumID == aquarium_id).first()
    if not aquarium:
        raise HTTPException(status_code=404, detail="Aquarium not found")
    db.delete(aquarium)
    db.commit()
    return {"message": "Aquarium deleted successfully"}

@app.delete("/sensors/{sensor_id}/")
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(IoTSensor).filter(IoTSensor.SensorID == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    db.delete(sensor)
    db.commit()
    return {"message": "Sensor deleted successfully"}

@app.delete("/admin/users/{user_id}/")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Administrator).filter(Administrator.AdminID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.put("/admin/users/{user_id}/role/")
def update_user_role(user_id: int, new_role: str, db: Session = Depends(get_db)):
    user = db.query(Administrator).filter(Administrator.AdminID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if new_role not in ["Administrator", "Technician", "Client"]:
        raise HTTPException(status_code=400, detail="Invalid role specified")
    
    user.Role = new_role
    db.commit()
    db.refresh(user)
    return {"message": f"User role updated to {new_role}"}

def log_system_operation(db: Session, operation: str, user_id: int, details: str = None):
    new_log = SystemLog(Operation=operation, UserID=user_id, Details=details)
    db.add(new_log)
    db.commit()

@app.get("/admin/logs/")
def get_system_logs(db: Session = Depends(get_db)):
    logs = db.query(SystemLog).order_by(SystemLog.Timestamp.desc()).all()
    return logs

@app.get("/admin/reports/")
def generate_system_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    logs = db.query(SystemLog).filter(
        SystemLog.Timestamp >= start,
        SystemLog.Timestamp <= end
    ).order_by(SystemLog.Timestamp.desc()).all()
    
    report = [{"Operation": log.Operation, "Timestamp": log.Timestamp, "UserID": log.UserID, "Details": log.Details} for log in logs]
    return {"report": report, "count": len(report)}

@app.get("/api/sensor-data", response_model=List[SensorDataResponse])
def get_all_sensor_data(db: Session = Depends(get_db)):
    data = db.query(SensorDataInDB).all()
    if not data:
        raise HTTPException(status_code=404, detail="No sensor data found")
    return data

@app.get("/api/sensor-data/{sensor_id}", response_model=List[SensorDataResponse])
def get_sensor_data_by_id(sensor_id: int, db: Session = Depends(get_db)):
    data = db.query(SensorDataInDB).filter(SensorDataInDB.sensor_id == sensor_id).all()
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for sensor_id {sensor_id}")
    return data

@app.get("/api/sensor-data/filter", response_model=List[SensorDataResponse])
def get_sensor_data_by_time_range(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    data = db.query(SensorDataInDB).filter(
        SensorDataInDB.timestamp >= start,
        SensorDataInDB.timestamp <= end
    ).all()
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for the given time range ({start_date} to {end_date})")
    
    return data

def assign_technician_to_aquarium(technician_id: int, aquarium_id: int, db: Session):
    technician = db.query(Technician).filter(Technician.TechnicianID == technician_id).first()
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")
    if technician.Availability != "Available":
        raise HTTPException(status_code=400, detail="Technician is not available")
    
    aquarium = db.query(Aquarium).filter(Aquarium.AquariumID == aquarium_id).first()
    if not aquarium:
        raise HTTPException(status_code=404, detail="Aquarium not found")
    
    aquarium.TechnicianID = technician_id
    db.commit()
    return {"message": "Technician assigned successfully"}

@app.post("/api/data", response_model=SensorDataResponse)
def receive_data(sensor_data: SensorData, db: Session = Depends(get_db)):
    print(f"Received data: Temperature = {sensor_data.temperature}, Humidity = {sensor_data.humidity}")

    sensor_id = sensor_data.sensor_id  

    new_sensor_data = SensorDataInDB(
        temperature=sensor_data.temperature,
        humidity=sensor_data.humidity,
        sensor_id=sensor_id  
    )
    db.add(new_sensor_data)
    db.commit()
    db.refresh(new_sensor_data) 

    return new_sensor_data 

@app.get("/api/temperature-trend/{sensor_id}", response_model=SensorTrendReport)
def analyze_trends(sensor_id: int, db: Session = Depends(get_db)):
    data = db.query(SensorDataInDB).filter(SensorDataInDB.sensor_id == sensor_id).all()
    timestamps = np.array([d.timestamp.timestamp() for d in data]).reshape(-1, 1)
    temperatures = np.array([d.temperature for d in data])
    
    model = LinearRegression()
    model.fit(timestamps, temperatures)
    
    trend = model.coef_[0]
    if trend > 0:
        trend_description = "З часом температура підвищується."
    elif trend < 0:
        trend_description = "З часом температура знижується."
    else:
        trend_description = "Температура стабільна протягом тривалого часу."

    return {
        "sensor_id": sensor_id, 
        "coefficient": float(trend), 
        "trend_description": trend_description
    }


@app.get("/api/data/sensors/{sensor_id}/value/")
def get_sensor_value(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(IoTSensor).filter(IoTSensor.SensorID == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor with ID {sensor_id} not found")
    
    return {"value": sensor.Value}