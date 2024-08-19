# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################



# Start at the homepage.
# List all the available routes.

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )



@app.route("/api/v1.0/precipitation")
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
# to a dictionary using date as the key and prcp as the value.
# https://github.com/python-restx/flask-restx/issues/115
def precipitation():

    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= query_date).all()

    session.close()

    prcp_dict = {date: prcp for date, prcp in prcp_data}
    
# Return the JSON representation of your dictionary.
    return jsonify(prcp_dict)



@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset.
def stations():

    session = Session(engine)

    results = session.query(station.station).all()
    
    session.close()

    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
def tobs():

    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    temp_data = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= query_date).all()

    session.close()

    temps = list(np.ravel(temp_data))
    
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

#1 For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#2 For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
def temps(start, end=None):

    session = Session(engine)

    if end is None:
        end = dt.date(9999, 12, 31).strftime("%Y-%m-%d")

    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    temp_stats = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()

    session.close()

    temps = {
        "TMIN": sel[0][0],
        "TAVG": sel[0][1],
        "TMAX": sel[0][2]
    }
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)