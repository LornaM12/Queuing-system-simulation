# import modules
import math
import random


# Initialize the maximum number of customers
Q_LIMIT = 100

# Initialize the server status
BUSY = 1
IDLE = 0

# Initialize variables used in the simulation
next_event_type = num_customers_delayed = num_delays_required = num_events = num_in_q = server_status = 0
area_num_in_q = area_server_status = mean_inter_arrival = mean_service = sim_time = time_last_event = total_of_delays = 0.0
time_arrival = [0.0] * (Q_LIMIT + 1)

# List to store the next event time for all 3 events: arrival, departure and end of simulation
time_next_event = [0.0] * 3

# Input and Output file
infile = open("mm1.in", "r")
outfile = open("mm1.out", "w")


# Function to initialize simulation variables
def initialize():
    global sim_time, server_status, num_in_q, time_last_event, num_customers_delayed, total_of_delays, area_num_in_q, area_server_status, time_next_event

    # Current simulation time
    sim_time = 0.0
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0
    num_customers_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0
    time_next_event[1] = sim_time + expon(mean_inter_arrival)
    time_next_event[2] = 1.0e+30


# Function to determine the next event
def timing():
    global sim_time, next_event_type

    min_time_next_event = 1.0e+29
    next_event_type = 0

    # Loop through events to determine the next event
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i

    # If event list is empty, exit the program
    if next_event_type == 0:
        outfile.write(f"Event list empty at time {sim_time}")
        exit(1)
    # Time of next event
    sim_time = min_time_next_event


# Function to update time and statistics of the simulation
def update_time_avg_stats():
    global sim_time, time_last_event, num_in_q, server_status, area_num_in_q, area_server_status

    # Compute time since last event, and update last-event-time marker.
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time

    # Update area under number-in-queue function.
    area_num_in_q += num_in_q * time_since_last_event

    # Update area under server-busy indicator function.
    area_server_status += server_status * time_since_last_event


# Function for arrival event
def arrive():
    global num_in_q, server_status, time_next_event, num_customers_delayed, total_of_delays

    time_next_event[1] = sim_time + expon(mean_inter_arrival)
    if server_status == BUSY:  # increase number of customers in q
        num_in_q += 1
        if num_in_q > Q_LIMIT:
            outfile.write(f"\nOverflow of the array time_arrival at time {sim_time}")
            exit(2)
        time_arrival[num_in_q] = sim_time
    else:
        delay = 0.0
        total_of_delays += delay
        num_customers_delayed += 1
        server_status = BUSY
        time_next_event[2] = sim_time + expon(mean_service)


# Function for departure event
def depart():
    global num_in_q, server_status, time_next_event, num_customers_delayed, total_of_delays, area_num_in_q, area_server_status

    if num_in_q == 0:
        server_status = IDLE
        time_next_event[2] = 1.0e+30
    else:
        num_in_q -= 1
        delay = sim_time - time_arrival[1]
        total_of_delays += delay
        num_customers_delayed += 1
        time_next_event[2] = sim_time + expon(mean_service)
        for i in range(1, num_in_q + 1):
            time_arrival[i] = time_arrival[i + 1]


def report():
    # Compute and write estimates of desired measures of in the output file.
    global total_of_delays, num_customers_delayed, area_num_in_q, sim_time, area_server_status
    outfile.write("\n\nAverage delay in queue%11.3f minutes\n\n" % (total_of_delays / num_customers_delayed))
    outfile.write("Average number in queue%10.3f\n\n" % (area_num_in_q / sim_time))
    outfile.write("Server utilization%15.3f\n\n" % (area_server_status / sim_time))
    outfile.write("Time simulation ended%12.3f minutes" % sim_time)


def expon(mean):
    return -mean * math.log(random.random())


if __name__ == '__main__':
    # Open input and output files.
    # Specify the number of events for the timing function.
    num_events = 2
    # Read input parameters.
    mean_inter_arrival, mean_service, num_delays_required = map(float, infile.readline().split())

    # Write report heading and input parameters.
    outfile.write("Single-server queueing system\n\n")
    outfile.write("Mean inter_arrival time%11.3f minutes\n\n" % mean_inter_arrival)
    outfile.write("Mean service time%16.3f minutes\n\n" % mean_service)
    outfile.write("Number of customers%14d\n\n" % num_delays_required)

    # Initialize the simulation.
    initialize()

    # Run the simulation while more delays are still needed.
    while num_customers_delayed < num_delays_required:
        # Determine the next event.
        timing()

        # Update time-average statistical accumulators.
        update_time_avg_stats()

        # Invoke the appropriate event function.
        if next_event_type == 1:
            arrive()
        elif next_event_type == 2:
            depart()

    # Invoke the report generator and end the simulation.
    report()

    # Close input and output files.
    infile.close()
    outfile.close()
