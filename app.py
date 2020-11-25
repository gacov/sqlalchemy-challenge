#Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
import re

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

#Save tables references
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create session
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Routes

# Function temprange will take start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for such date range
def temprange(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#Set Flask Routes

@app.route("/")
def home():
    return(f"""
        --------------------------------
        The routes available are:
    
    
        /api/v1.0/precipitation
        /api/v1.0/stations
        /api/v1.0/tobs
        /api/v1.0/<start>
        /api/v1.0/<start>/<end>
        --------------------------------
        for /api/v1.0/<start> please insert date in the YYYY-MM-DD format to retrieve data from such date to 2017-08-23 (the latest available).
        
        Alternatively, you can define a range of dates by typing /api/v1.0/START/END
    """)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session 
    session = Session(engine)

     # Query Measurement
    results = (
        session.query(Measurement.date, Measurement.tobs)
                      .order_by(Measurement.date)
                )
    
    # Create a dictionary
    precipitation_date_tobs = []
    for eachrow in results:
        dt_dict = {}
        dt_dict["date"] = eachrow.date
        dt_dict["tobs"] = eachrow.tobs
        precipitation_date_tobs.append(dt_dict)

    return jsonify(precipitation_date_tobs)

@app.route("/api/v1.0/stations")
def stations():
    # Create session 
    session = Session(engine)

    # Query Stations
    results = session.query(Station.name).all()

    # Convert to normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session 
    session = Session(engine)

    # getting latest date and calculate one year back date
    latestdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    latestdatestr = str(latestdate)
    latestdatestr = re.sub("'|,", "",latestdatestr)
    latestdate = dt.datetime.strptime(latestdatestr, '(%Y-%m-%d)')
    oneyearback = dt.date(latestdate.year, latestdate.month, latestdate.day) - dt.timedelta(days=365)
     
    # getting station names and their observation counts sorted descending and select most active station
    stations = (session.query(Measurement.station, func.count(Measurement.station))
                             .group_by(Measurement.station)
                             .order_by(func.count(Measurement.station).desc())
                             .all())
    
    mostactive = stations[0][0]


    # Return a list of tobs for the year before the final date
    tobsresults = (session.query(Measurement.station, Measurement.date, Measurement.tobs)
                      .filter(Measurement.date >= oneyearback)
                      .filter(Measurement.station == mostactive)
                      .all())

    # Create JSON results
    tobs = []
    for result in tobsresults:
        line = {}
        line["Date"] = result[1]
        line["Station"] = result[0]
        line["Temperature"] = int(result[2])
        tobs.append(line)

    
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start_only(start):

    # Create session 
    session = Session(engine)

    # Date Range
    dateend = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    dateendstr = str(dateend)
    dateendstr = re.sub("'|,", "",dateendstr)
    print (dateendstr)

    datebeg = session.query(Measurement.date).first()
    datebegstr = str(datebeg)
    datebegstr = re.sub("'|,", "",datebegstr)
    print (datebegstr)

    results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    				 	  .filter(Measurement.date >= start).all())

    tmin =results[0][0]
    tavg ='{0:.4}'.format(results[0][1])
    tmax =results[0][2]
    

    return jsonify(f"""From {start} to {dateendstr}, the lowest Temperature was: {tmin}F, the average Temperature was: {tavg}F and the max Temperature was: {tmax}F""")

    
   

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    # Create session 
    session = Session(engine)

    # Date Range
    dateend = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    dateendstr = str(dateend)
    dateendstr = re.sub("'|,", "",dateendstr)
    print (dateendstr)

    datebeg = session.query(Measurement.date).first()
    datebegstr = str(datebeg)
    datebegstr = re.sub("'|,", "",datebegstr)
    print (datebegstr)

    results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    					  .filter(Measurement.date >= start)
    				  	  .filter(Measurement.date <= end).all())

    tmin =results[0][0]
    tavg ='{0:.4}'.format(results[0][1])
    tmax =results[0][2]
    
    return jsonify(f"Between {start} and {end}, the lowest Temperature was: {tmin}F, the average Temperature was: {tavg}F and the max Temperature was: {tmax}F""")

if __name__ == "__main__":
    app.run(debug=True)    
