#!/usr/bin/env python
import argparse
import json
import random
import string
from flask import Flask, render_template, send_from_directory, make_response, request, url_for, redirect
from run_back_end import RunBackEnd
from multiprocessing import Process

app = Flask(__name__)
data= dict()
surveyData=dict()
args=None

@app.route("/instructions.html")
def instructions():
    survey_duration = 10*60*60 #10 hours to prevent retaking

    if app.debug: 
        mturk_id = args.ID
    else:
        mturk_id = request.cookies.get('mturk_id','')
        if mturk_id == '':
            #generate a cookie with user's ID
            mturk_id = ''.join(random.choice(string.ascii_uppercase +
                                           string.digits) for _ in range(6))

    resp = make_response(render_template('instructions.html'))
    resp.set_cookie('mturk_id', mturk_id, max_age=survey_duration, path='/')

    back_end = RunBackEnd()
    p = Process(target=back_end.runBackEnd, args=(mturk_id,))
    p.start()
    data[mturk_id] = p

    return resp

@app.route("/")
def consent():
    return make_response(render_template('consent.html'))  

@app.route("/index.html")
def index():
    return make_response(render_template('index.html'))  

@app.route("/finish.html")
def finish():
    return make_response(render_template('finish.html')) 

@app.route("/survey.html")
def survey():
    if app.debug: 
        data[args.ID].terminate()
    else:
        mturk_id = request.cookies.get('mturk_id','')
        if mturk_id != '':
            data[mturk_id].terminate()
        
    return make_response(render_template('survey.html')) 

@app.route("/submit_survey",methods=['POST'])
def submit_survey():
  mturk_id = request.cookies.get('mturk_id','')
  surveyData[mturk_id] = request.form
  with open('/home/ubuntu/results/survey_{}.json'.format(mturk_id), 'w') as outfile:
    json.dump(surveyData, outfile)
  print("User {} submitted the survey".format(mturk_id))
  return """
            <br><h1>Thank you participating in this study! Your Mechanical Turk ID is: {}</h1>
         """.format(mturk_id)

if __name__ == "__main__":

    app.run(host='0.0.0.0', port="8080")


