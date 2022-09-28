import simpy
import random
import statistics

wait_times = []
seats = 120

class Airport(object):
    
    def __init__(self, env, numW_gate, numW_security, numW_checkin): # constructor for the airport object
        self.env = env
        self.wGate = simpy.Resource(env, numW_gate) # .Resource() allows us to restrict the usage of the variable -- gate worker needs to be requested, if unvailable, request must wait until work is available
        self.wSecurity = simpy.Resource(env, numW_security)
        self.wCheckin = simpy.Resource(env, numW_checkin)

    def check_in(self, passenger):
        yield self.env.timeout(random.randint(2, 5))

    def pass_security(self, passenger):
        yield self.env.timeout(random.randint(8, 12))

    def enter_gate(self, passenger):
        yield self.env.timeout(random.randint(1, 3))
        
def travel(env, passenger, airport):
    arrival_time = env.now

    with airport.wCheckin.request() as request:
        yield request
        yield env.process(airport.check_in(passenger))

    with airport.wSecurity.request() as request:
        yield request
        yield env.process(airport.pass_security(passenger))

    with airport.wGate.request() as request:
        yield request
        yield env.process(airport.enter_gate(passenger))

    wait_times.append(env.now - arrival_time)

def manage_airport(env, numW_gate, numW_security, numW_checkin):
    airport = Airport(env, numW_gate, numW_security, numW_checkin)

    for passenger in range(1):
        env.process(travel(env, passenger, airport))
    
    while True:
        yield env.timeout(1.00)

        passenger += 1
        env.process(travel(env, passenger, airport))

def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

def get_user_input():
    numW_gate = input("How many workers at the gate? : ")
    numW_security = input("How many works at security? : ")
    numW_checkin = input("How many workers at check-in? : ")

    params = [numW_gate, numW_security, numW_checkin]
    if all(str(i).isdigit() for i in params):
        params = [int(x) for x in params]
    else:
        print("Could not parse input. Simulation will use default values:",
              "\n1 at gate, 3 at security, 2 at check-in.", )
        params = [1, 3, 2]
    return params

def main():
    random.seed(123)
    numW_gate, numW_security, numW_checkin = get_user_input()

    env = simpy.Environment()
    env.process(manage_airport(env, numW_gate, numW_security, numW_checkin))
    env.run(until = 3600)

    mins, secs = get_average_wait_time(wait_times)
    print("Running simulation...",
          f"\nThe average wait time is {mins} minutes and {secs} seconds.", )

if __name__ == "__main__":
    main()
    
