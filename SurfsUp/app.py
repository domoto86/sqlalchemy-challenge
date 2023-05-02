# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, MetaData, Table
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(autoload_with = engine)

# reflect the tables
print(Base.classes.keys())

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
def welcome():
    return(
        f'Available Routes: <br/>'
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'/api/v1.0/tobs <br/>'
        f'/api/v1.0/<start> <br/>'
        f'/api/v1.0/<start>/<end> <br/>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    last_year = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    results_date = session.query(Measurement.date, func.sum(Measurement.prcp)).filter(Measurement.date >= last_year).group_by(Measurement.date)
    session.close()
    dates_last_year = list(np.ravel(results_date))
    precipitation_dict = {date: prcp for date, prcp in results_date}
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results_stations = session.query(Station.id, Station.station).all()
    session.close
    stations_all = list(np.ravel(results_stations))
    stations_dict = {station: id for station, id in results_stations}
    return jsonify(stations_dict)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    last_year = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    most_active = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()[0]
    results_tob = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active).filter(Measurement.date >= last_year).all()
    session.close
    tobs_all = list(np.ravel(results_tob))
    stations_tob = {date: tobs for date, tobs in results_tob}
    return jsonify(stations_tob)

@app.route('/api/v1.0/<start>')
def search_start_date(start):
    session = Session(engine)
    results_start = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close
    start_dict = {'Minimum Temperature: ': results_start[0][0], 'Maximum Temperature: ': results_start[0][1], 'Average Temperature: ': results_start[0][0]}
    return jsonify(start_dict)

@app.route('/api/v1.0/<start>/<end>')
def search_start_end_date(start, end):
    session = Session(engine)
    results_start_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close
    start_end_dict = {'Minimum Temperature: ': results_start_end[0][0], 'Maximum Temperature: ': results_start_end[0][1], 'Average Temperature: ': results_start_end[0][0]}
    return jsonify(start_end_dict)

if __name__ == "__main__":
    app.run(debug=True)