from scheduler import Scheduler
from typing import List, Callable
from matplotlib import pyplot as plt


class Simulator:
    """
    Simulates a series of process schedulers on sets
    of processes.
    """

    @staticmethod
    def run(scheduler: Scheduler, verbose:int = 0) -> dict:
        """
        Runs a scheduler and processes the results
        :param scheduler:
        :param verbose: the verbose setting for the simulator
        :return: the dictionary of stats from the scheduler
        """
        # Run the scheduler
        stats = scheduler.run()

        # Prints summary stats
        if verbose:
            print(f"---- RUNNING THE {stats['title']} ALGORITHM ----")
            print(f"\tAverage Completion Time: {stats['avg_comp_time']}")
            print(f"\tAverage Wait Time: {stats['avg_wait_time']}")

        return stats

    @staticmethod
    def compare(schedulers: List[Scheduler], visuals: List[Callable[[dict], None]]) -> dict:
        """
        Compares a set of schedulers against each other
        :param schedulers: A list of Scheduler objects to use
        :param visuals: A list of functions which create visualization with
                        the history dictionary.
        :return: A dictionary containing the summary stats
        """
        assert len(schedulers) > 0, 'NO SCHEDULERS PROVIDED FOR COMPARE'
        history = {}
        for scheduler in schedulers:
            stats = scheduler.run()
            title = stats['title']
            stats.pop('title')
            history[title] = stats

        for visual in visuals:
            visual(history)

        return history


def bar(history: dict) -> None:
    """
    Creates a bar chart using a Simulator history dictionary
    :param history: a dictionary from a Simulator
    """
    def add_labels(x, y, ax):
        for i in range(len(x)):
            ax.text(i, y[i] // 2, y[i], ha='center')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    labels = list(history.keys())

    # Plot average completion time data
    comp_times = [history[lbl]['avg_comp_time'] for lbl in labels]
    #comp_colors = [cm.jet(1. * i / x) for i, x in enumerate(comp_times)]
    ax1.bar(labels, comp_times, label=labels)
    ax1.set_ylabel('Time')
    ax1.set_xlabel('Scheduling Algorithm')
    ax1.set_title('Average Completion Time')
    add_labels(labels, comp_times, ax1)

    # Plot wait times
    wait_times = [history[lbl]['avg_wait_time'] for lbl in labels]
    ax2.bar(labels, wait_times, label=labels)
    ax2.set_ylabel('Time')
    ax2.set_xlabel('Scheduling Algorithm')
    ax2.set_title('Average Waiting Time')
    add_labels(labels, wait_times, ax2)

    plt.show()


def time_slice_bar(history: dict) -> None:
    print(history)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    labels = list(history.keys())

    time_slices = []
    comp_times = []
    wait_times = []
    for lbl in labels:
        time_slices.append(history[lbl]['time_slice'])
        comp_times.append(history[lbl]['avg_comp_time'])
        wait_times.append(history[lbl]['avg_wait_time'])

    ax1.plot(time_slices, comp_times)
    ax1.set_ylabel('Time')
    ax1.set_xlabel('Time Slice')
    ax1.set_title('Average Completion Time')

    ax2.plot(time_slices, wait_times)
    ax2.set_ylabel('Time')
    ax2.set_xlabel('Time Slice')
    ax2.set_title('Average Waiting Time')

    plt.show()
