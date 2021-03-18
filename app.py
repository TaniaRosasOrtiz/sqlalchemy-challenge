# 1. import dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
import re
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists 

# SETUP DATABASE #####################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# ####################################

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Routes availables:<br/>"
            f"Precipitation path /api/v1.0/precipitation<br/>"
            f"Stations path /api/v1.0/stations<br/>"
            f"Temperatures path /api/v1.0/tobs<br/>"
            f"Temperatures path with time start /api/v1.0/start<br/>"
            f"Temperatures path with time range /api/v1.0/start/end<br/>")

# 4. Define what to do when a user hits the different routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_lists = []
    for date, prcp in prcp_data:
        prcp_dic = {}
        prcp_dic["date"] = date
        prcp_dic["prcp"] = prcp
        prcp_lists.append(prcp_dic)

    # Return the JSON representation of your dictionary.
    return jsonify(prcp_lists)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Station.name).order_by(Station.name).all()
    
    session.close()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))

    # Return a JSON list of stations from the dataset.
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the dates and temperature observations of the most active station for the last year of data.

    # Get latest date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    yearago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= yearago_date).\
        order_by(Measurement.date).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    tobs_year = []
    for date, tobs in results:
        tobs_dic = {}
        tobs_dic["date"] = date
        tobs_dic["tobs"] = tobs
        tobs_year.append(tobs_dic)

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_year)


@app.route("/api/v1.0/<start>") 
def start_input(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get date 
    date_last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_last_str = str(date_last)
    date_last_str = re.sub("'|,", "",date_last_str)
    print (date_last_str)

    date_first = session.query(Measurement.date).first()
    date_first_str = str(date_first)
    date_first_str = re.sub("'|,", "",date_first_str)
    print (date_first_str)


    # Validate start date 
    valid_date = session.query(exists().where(Measurement.date == start)).scalar()
 
    if valid_date:

    	results = (session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all())

    	tob_min =results[0][0]
    	tob_avg ='{0:.4}'.format(results[0][1])
    	tob_max =results[0][2]
    
    	result_printout =( ['Date to look: ' + start,
    						'Min Temperature: '  + str(tob_min) + ' F',
    						'Max Temperature: ' + str(tob_max) + ' F',
    						'Average Temperature: ' + str(tob_avg) + ' F'])
    	return jsonify(result_printout)

    return jsonify({"error": f"Input date {start} not valid"}), 404
   

@app.route("/api/v1.0/<start>/<end>")
def start_end_input(start, end):

     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get date 
    date_last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_last_str = str(date_last)
    date_last_str = re.sub("'|,", "",date_last_str)
    print (date_last_str)

    date_first = session.query(Measurement.date).first()
    date_first_str = str(date_first)
    date_first_str = re.sub("'|,", "",date_first_str)
    print (date_first_str)

    # Validate start date 
    valid_date_start = session.query(exists().where(Measurement.date == start)).scalar()
 	
    # Validate end date 
    valid_date_end = session.query(exists().where(Measurement.date == end)).scalar()

    if valid_date_start and valid_date_end:

    	results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

    	tob_min =results[0][0]
    	tob_avg ='{0:.4}'.format(results[0][1])
    	tob_max =results[0][2]

    	result_printout =( ['Date Range: ' + start + ' ' + end,
    						'Min Temperature: '  + str(tob_min) + ' F',
    						'Max Temperature: ' + str(tob_max) + ' F',
    						'Average Temperature: ' + str(tob_avg) + ' F'])
    	return jsonify(result_printout)

if __name__ == "__main__":
    app.run(debug=True)
