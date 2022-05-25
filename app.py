import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import json

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Home_page():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f'<a href = "/api/v1.0/precipitation">precipitation_api</a><br/>'
        f"/api/v1.0/station"
        f"/api/v1.0/tobs"
        f"/api/v1.0/end_date"
        f"/api/v1.0/tobs"
        
    )


@app.route("/api/v1.0/precipitation")
def Measurement_page():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Convert the query results to a dictionary using
    #`date` as the key and `prcp` as the value.

    tuple_list = session.query(Measurement.prcp, Measurement.date).all()
    data_dict = {}
    for row in tuple_list:
        prcp = row[0]
        date = row[1]
        data_dict[date] = prcp
    
    
    session.close()
    
    return jsonify(data_dict)
    


    
@app.route("/api/v1.0/station")
def Station_page():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    results = session.query(Station).all()
#    station_list = []
#     for row in results:
#         station_dict = row.__dict__
#         station_list.append(station_dict)
    

    session.close()

    station_list = []
    for row in results:
       # station_dict = str(row.__dict__)
        station_dict = {'latitude': row.latitude,
        'id': row.id,
        'elevation': row.elevation,
        'longitude': row.longitude,
        'station': row.station,
        'name': row.name}
        station_list.append(station_dict)
        
    return jsonify(station_list)
   
@app.route("/api/v1.0/tobs")
def Tobs_page():
    
    session = Session(engine)

    
    
    station_gb = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc())

    results = station_gb.first()
    most_active_station = {"station": results[0],"activity": results[1]}
    
    
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    station_temp = session.query(Measurement.station, Measurement.date,Measurement.tobs,Station.name).join(Station, Measurement.station == Station.station).filter(Measurement.station ==most_active_station["station"]).filter(Measurement.date >= prev_year).order_by(Measurement.station).all()
    
    temp_list = []
    
    for row in station_temp:
        
        active_station_temp = { "Station ID": row[0],
                                "Date": row[1],
                                "Temp": row[2],
                                "Station Name":row[3]
                               }
        temp_list.append(active_station_temp)
        

    return jsonify(temp_list)

   
@app.route("/api/v1.0/<start_date>")
def Start_stats(start_date): 
    active_max = session.query(Measurement.station, func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    order_by(Measurement.station).first()



    active_min = session.query(Measurement.station, func.min(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    order_by(Measurement.station).first()



    active_avg = session.query(Measurement.station, func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    order_by(Measurement.station).first()
    
    


    
    max_dict = {"TMAX": active_max[1],
                "Station": active_max[0]
                
    }
    
    min_dict = {"TMIN": active_min[1],
                "Station": active_min[0]
               }
    
    avg_dict = {"TAVG": active_avg[1]
                }
    
    stat_list = [max_dict, min_dict, avg_dict] 
    
    session.close()
   
    return jsonify(stat_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def Start_end_stats(start_date, end_date): 
    active_max = session.query(Measurement.station, func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).\
    order_by(Measurement.station).first()



    active_min = session.query(Measurement.station, func.min(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).\
    order_by(Measurement.station).first()



    active_avg = session.query(Measurement.station, func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).\
    order_by(Measurement.station).first()
    
    


    
    max_dict = {"TMAX": active_max[1],
                "Station": active_max[0]
                
    }
    
    min_dict = {"TMIN": active_min[1],
                "Station": active_min[0]
               }
    
    avg_dict = {"TAVG": active_avg[1]
                }
    
    stat_list = [max_dict, min_dict, avg_dict] 
    
    session.close()
   
    return jsonify(stat_list)


if __name__ == '__main__':
    app.run(debug=True)




# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
   
