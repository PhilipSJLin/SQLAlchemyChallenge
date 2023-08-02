# Import the dependencies.

import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify 

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()

# Save references to each table
Base.prepare(engine, reflect=True)

# Create our session (link) from Python to the DB
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    # List all the available routes
    return (
        f"Welcome to Philip's SQL-Alchemy Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/insert(yyyy-mm-dd)<start><br/>"
        f"/api/v1.0/insert(yyyy-mm-dd)<start>/(yyyy-mm-dd)<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set.
    mostrecent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    print(mostrecent_date)

    # Calculate the date one year from the last date in data set.
    latest_date = dt.datetime.strptime(mostrecent_date[0], '%Y-%m-%d').date()
    start_date = latest_date - dt.timedelta(days=365)

    # Perform a query to retrieve all the date and precipitation values
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).order_by(measurement.date).all()

    # Close session
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    prcp_dict = {} 
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    
    # Return the JSON representation of your dictionary for the last year in the database.
    return jsonify(prcp_dict)

# Create a route that returns a JSON list of stations from the database
@app.route("/api/v1.0/stations")
def stations(): 
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve all of the station values
    total_stations = session.query(station.id, station.station, station.name).all()
    
    # Close session
    session.close()  
    
    # Convert the query results to a dictionary using for loop
    list_stations = []

    for stat in total_stations:
        station_dict = {}

        station_dict["id"] = stat[0]
        station_dict["station"] = stat[1]
        station_dict["name"] = stat[2]

        list_stations.append(station_dict)

    # Return a JSON list of stations from the dataset.
    return jsonify(list_stations)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs") 
def tobs():

    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()    
    latest_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d').date()
    start_date = latest_date - dt.timedelta(days=365)
    
    # Create query for all tobs for 12 months from most recent date
    stationtemps_lastyear = session.query(measurement.tobs).\
                    filter(measurement.date >= '2016-08-23').\
                    filter(measurement.station == 'USC00519281').all()
    
    # Close session
    session.close() 
    
    tobs_values = []
    for date, tobs in stationtemps_lastyear:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_values.append(tobs_dict) 
          
    return jsonify(tobs_values) 

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
# Query TMIN, TAVG, TMAX for specified start for all dates greater than or equal to start date
@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)
    start_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    tobs_start = []
    for min, avg, max in start_results:
        tobs_start_dict = {}
        tobs_start_dict["TMIN"] = min
        tobs_start_dict["TAVG"] = avg
        tobs_start_dict["TMAX"] = max
        tobs_start.append(tobs_start_dict) 

    return jsonify(tobs_start)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
# Query TMIN, TAVG, TMAX for specified start and end date for dates from start to end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    
    session = Session(engine)
    start_end_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    
    start_end_tobs = []
    for min, avg, max in start_end_results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["TMIN"] = min
        start_end_tobs_dict["TAVG"] = avg
        start_end_tobs_dict["TMAX"] = max
        start_end_tobs.append(start_end_tobs_dict) 
        
    return jsonify(start_end_tobs)

if __name__ == "__main__":
    app.run(debug=True)

# Close session
session.close()