# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 21:11:44 2020

@author: rajes
"""

from flask import Flask, flash, redirect, render_template, request, session, abort
app = Flask(__name__)

import simpy
import random
import statistics

wait_times = []
WASHTIME = 15      # Minutes it takes to clean a car

class Carwash(object):

    def __init__(self, env, num_machines, washtime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime

    def wash(self, car):
        """The washing processes. It takes a ``car`` processes and tries
        to clean it."""
        yield self.env.timeout(WASHTIME)



def car(env, name, cw):

    print('%s arrives at the carwash at %.2f.' % (name, env.now))
    arrive =  env.now
    
    #print('arrive value=', arrive)
    with cw.machine.request() as request:
        yield request

        print('%s enters the carwash at %.2f.' % (name, env.now))
        yield env.process(cw.wash(name))

        print('%s leaves the carwash at %.2f.' % (name, env.now))
        
        wait = env.now-arrive
        print ('%s waited for %.2f.' % (name, wait))
        
    wait_times.append(env.now - arrive) 
    #print('wait_times-',wait_times)
    
    
def setup(env, num_machines, washtime, t_inter):
    """Create a carwash, a number of initial cars and keep creating cars
    approx. every ``t_inter`` minutes."""
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    # Create 4 initial cars
    for i in range(4):
        env.process(car(env, 'Car %d' % i, carwash))

    # Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(t_inter-2, t_inter+2))
        i += 1
        env.process(car(env, 'Car %d' % i, carwash))


def get_average_wait_time(wait_times):
    #print('---wait_times-1-',wait_times)
    average_wait = statistics.mean(wait_times)
    #print('---average_wait-2-',average_wait)
    # Pretty print the results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)



@app.route('/')
def main():
    #print('----in main mthd----')
    return render_template('create.html')


@app.route('/getData' ,methods=['POST'])
def getData():
    #print('Inside getdata function')
    if request.method == 'POST':
        
        #input values 
        RANDOM_SEED = 42
        #NUM_MACHINES = 2  # Number of machines in the carwash
        #T_INTER = 7       # Create a car every ~7 minutes
        #SIM_TIME = 20     # Simulation time in minutes



        NUM_MACHINES = request.form['nm']
        NUM_MACHINES = int(NUM_MACHINES)
        T_INTER = request.form['int']
        T_INTER = int(T_INTER)
        SIM_TIME = request.form['st']
        SIM_TIME = int(SIM_TIME)
    
        # Run the simulation
        print('\n Simulating ...\n ')
        env = simpy.Environment()
        env.process(setup(env, NUM_MACHINES, WASHTIME, T_INTER))
        # Execute!
        env.run(until=SIM_TIME)
    
        # View the results
        #print('wait_times-',get_average_wait_time(wait_times))
        mins, secs = get_average_wait_time(wait_times)
        result= f"The average wait time is {mins} minutes and {secs} seconds."
        print('\n',result)

    return render_template('result.html',result=result) 

if __name__ == '__main__':
    app.run(debug=True)
