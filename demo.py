from process import Process
from scheduler import Scheduler, FIFOScheduler, SJFScheduler, RoundRobinScheduler, SRTFScheduler
from simulator import Simulator, bar, time_slice_bar
import json


class SchedulerType:
    FIFO = 0
    SJF = 1
    RoundRobin = 2
    SRTFScheduler = 3


########################################################
# DEFINE CUSTOM EVENT LISTENERS TO PRINT OUT INTERNAL  #
# SCHEDULING INFORMATION                               #
########################################################
def step_end(process: Process, scheduler: Scheduler) -> None:
    """
    Prints a message about a process that just finished a step of
    scheduling
    :param process:   the process that just ran
    :param scheduler: the scheduler that ran process
    """
    pid = process.id
    start_time = scheduler.time
    time_ran = scheduler.step_time_ran
    print(f"RUN  - {pid:4} - At: {start_time:4} - Ran For: {time_ran:4}")


def process_done(process: Process, scheduler: Scheduler) -> None:
    """
    Prints a message about a process that just finished executing
    :param process:   the process that just ran
    :param scheduler: the scheduler that ran process
    """
    print(f"DONE - {process.id:4} - Ex. Time: {process.ex_time:4} - ", end="")
    print(f"Wait Time: {process.wait_time:4} - Comp. Time: {process.completion_time:4}\n")



########################################################
# DEFINE A SERIES OF TESTS TO SHOW DIFFERENT FEATURES  #
########################################################
def single_scheduler_test(input_file: str, scheduler_type: int, verbose: int = 1) -> dict:
    """
    Runs a single set of processes on a single scheduler.
    Doesn't generate any charts. Uses event listeners to demonstrate
    the internals of the schedulers.
    :param input_file: An input file containing info on the processes
    :param scheduler_type: The type of scheduler to use - Values comes
                           from Class SchedulerTypes
    :param verbose: The verbose setting to use
    :return: A dictionary containing the summary stats for the scheduler
    """
    # Read processes
    processes = Process.read_processes(input_file)

    # Create the scheduler
    schedulers = [
        FIFOScheduler(processes, verbose),
        SJFScheduler(processes, verbose),
        RoundRobinScheduler(processes, verbose, 5),
        SRTFScheduler(processes, verbose)
    ]
    scheduler = schedulers[scheduler_type]

    # Print a testing header
    print(f"----- RUNNING A SINGLE SCHEDULER TEST ON {scheduler.__class__.__name__} -----", end="\n\n")

    # Add event listeners to the scheduler
    scheduler.register_step_listener(step_end)
    scheduler.register_process_done_listener(process_done)

    # Run simulation and print out the summary statistics.
    stats = Simulator.run(scheduler)
    print(json.dumps(stats, sort_keys=False, indent=4))
    return stats


def basic_compare_test(input_file: str) -> None:
    """
    Runs a basic comparison test between the four schedulers.
    Creates a bar graph containing the summary results.
    :param input_file: A valid input file containing process info
    """
    print(f"----- RUNNING A BASIC COMPARISON TEST -----", end="\n\n")

    # Read processes
    processes = Process.read_processes(input_file)

    # Make schedulers
    verbose = 0
    schedulers = [
        FIFOScheduler(processes, verbose),
        SJFScheduler(processes, verbose),
        RoundRobinScheduler(processes, verbose, 5),
        RoundRobinScheduler(processes, verbose, 6),
        SRTFScheduler(processes, verbose)
    ]

    # Add event listeners
    for s in schedulers:
        s.register_step_listener(step_end)
        s.register_process_done_listener(process_done)

    # Add visualizations
    visuals = [
        bar
    ]

    # Run simulation
    stats = Simulator.compare(schedulers, visuals)
    print(json.dumps(stats, sort_keys=False, indent=4))


def round_robin_test() -> None:
    """
    Runs a comparison test to demonstrate the downside of Round Robin
    """
    print(f"----- RUNNING A TEST TO DEMONSTRATE ROUND ROBIN DOWNSIDE -----")

    # Read processes
    processes = Process.read_processes('test_data/roundrobin-test.txt')

    # Make schedulers
    verbose = 0
    schedulers = [
        FIFOScheduler(processes, verbose),
        SJFScheduler(processes, verbose),
        RoundRobinScheduler(processes, verbose, 1),
        SRTFScheduler(processes, verbose)
    ]

    # Add event listeners
    for s in schedulers:
        s.register_step_listener(step_end)
        s.register_process_done_listener(process_done)

    # Add visualizations
    visuals = [
        bar
    ]

    # Run simulation
    stats = Simulator.compare(schedulers, visuals)
    print(json.dumps(stats, sort_keys=False, indent=4))


def time_slice_test(input_file: str) -> None:
    """
    Runs a simple test to compare the effects of different time
    slices for the Round Robin scheduler.
    :param input_file: A valid input file containing process info
    """
    min_slice, max_slice, inc = 1, 100, 1
    print(f"----- RUNNING A R.R. TIME SLICE COMPARISON TEST [{min_slice}:{max_slice}:{inc}] -----", end="\n\n")

    # Read processes
    processes = Process.read_processes(input_file)

    # Make schedulers
    verbose = 0
    schedulers = \
        [RoundRobinScheduler(processes, verbose, x) for x in range(min_slice, max_slice+1, inc)]

    # Add event listeners
    for s in schedulers:
        s.register_step_listener(step_end)
        s.register_process_done_listener(process_done)

    # Add visualizations
    visuals = [
        time_slice_bar
    ]

    # Run simulation
    stats = Simulator.compare(schedulers, visuals)
    #print(json.dumps(stats, sort_keys=False, indent=4))


def main():
    # Define a preset list of schedulers for convenience
    single_scheduler_test('test_data/simple-input.txt', SchedulerType.FIFO, verbose=2)

    # basic_compare_test('test_data/simple-input.txt')
    # basic_compare_test('test_data/sjf_test.txt')
    # basic_compare_test('test_data/srtf_test.txt')

    # round_robin_test()

    # time_slice_test('test_data/simple-input.txt')



if __name__ == '__main__':
    main()
