# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model

# Base = declarative_base()
Base = automap_base()

# # reflect the tables

# Base.prepare(autoload_with=engine)

Base.prepare(engine, reflect=True)
Base.classes.keys()

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

# 1. /

# Start at the homepage.

# List all the available routes.

@app.route("/")
def welcome():
    """Welcome to the Climate Analysis of Hawaii API!"""
    return(
        f"Welcome to the Climate Analysis of Hawaii API!<br/>"
        f"In order to access the information, you will need to copy the route you would like to travel on and paste it at the end of the URL in your browser<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD)"
    )

# 2. /api/v1.0/precipitation

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').\
            filter(Measurement.date <= '2017-08-23').all()

    session.close()

    complete_prcp = []

    for date,prcp in scores:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp

        complete_prcp.append(prcp_dict)

    return jsonify(complete_prcp)

# 3. /api/v1.0/stations

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    data = [Station.station, Station.name,Station.latitude,Station.longitude,Station.elevation]
    query = session.query(*data).all()
    session.close()

    stations = []
    for station,name,latitude,longitude,elevation in query:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        stations.append(station_dict)

    return jsonify(stations)

# 4. /api/v1.0/tobs

# Query the dates and temperature observations of the most-active station for the previous year of data.

# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    temp_query = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
            filter(Measurement.date <= '2017-08-23').all()

    session.close()

    complete_tobs = []

    for date,tobs in temp_query:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["prcp"] = tobs

        complete_tobs.append(tobs_dict)

    return jsonify(complete_tobs)

# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)
    start_query = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min,avg,max in start_query:
        temps_dict = {}
        temps_dict["Minimum Temperature"] = min
        temps_dict["Average Temperature"] = avg
        temps_dict["Maximum Temperature"] = max
        temps.append(temps_dict)

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def temp_finish(start, end):
    session = Session(engine)
    end_query = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps_end = []
    for min,avg,max in end_query:
        temps_dict = {}
        temps_dict["Minimum Temperature"] = min
        temps_dict["Average Temperature"] = avg
        temps_dict["Maximum Temperature"] = max
        temps_end.append(temps_dict)

    return jsonify(temps_end)


if __name__ == '__main__':
    app.run(debug=True)