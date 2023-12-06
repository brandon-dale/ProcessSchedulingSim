from process import Process
import bisect
import copy

class Scheduler:
    """
    Interface Class for a Scheduling Algorithm
    """

    def __init__(self, processes: list, verbose:int = 1):
        """
`       Initializes a Scheduler object given a list of processes
        :param processes: A list of processes to run
        :param verbose: The verbose setting for simulations
            0 = silent mode - Don't print anything
            1 = done mode = only print info about a process when it is done
            2 = print process done info and info about each simulation step
        """
        # ---- Process Queues/Lists ---- #
        # Store all finished processes
        self._done_processes: list = []
        # Stores all runnable processes
        self._runnable: list = []
        # Stores all waiting processes in order
        self._waiting: list = []

        # ---- Scheduling Attributes ---- #
        # The current execution time
        self._time: int = 0
        # The verbose setting
        self._verbose:int = verbose
        # The currently executing process
        self._curr_process = None
        # The time the current process ran for
        self._step_time_ran = 0
        # The scheduling aggregation stats
        self.stats = {}

        # ---- Event Listeners ---- #
        # listener functions to call after a step of processing
        self._step_end_listeners = []
        # listener functions to call after a process is finished
        self._process_done_listeners = []
        # listener functions to call when a process arrives (wait -> runnable)
        self._process_arrive_listeners = []

        # Sort all processes into the correct lists
        for _p in processes:
            p = copy.deepcopy(_p)
            if p.arrival_time <= 0:
                self._runnable.append(p)
            else:
                self._waiting.append(p)
        self._waiting.sort()

    def run(self) -> dict:
        """
        Runs the scheduling algorithm until all processes
        are finished.
        :return: is a dictionary of summary statistics
        """
        # Run scheduler
        while not self.is_done:
            self.step()

        # Get summary statistics
        self.stats = {
            'avg_comp_time': 0,
            'avg_wait_time': 0,
            'num_processes_ran': 0
        }
        for process in self.done_processes:
            self.stats['avg_comp_time'] += process.completion_time
            self.stats['avg_wait_time'] += process.wait_time
            self.stats['num_processes_ran'] += 1
        self.stats['avg_comp_time'] /= self.stats['num_processes_ran']
        self.stats['avg_wait_time'] /= self.stats['num_processes_ran']

    def step(self) -> bool:
        """
        Virtual Method
        Runs a single step of the scheduling algorithm
        :return: True if the scheduler is done. Else False
        """
        raise NotImplementedError

    def get_next_process(self):
        """
        Virtual Method
        Gets the next process to run at the current time step.
        Child classes will implement fetching of next process.
        This part handles the case where the next process is
        in the waiting queue
        :return: The next process to be run
        """
        if len(self._runnable) == 0 and len(self._waiting) > 0:
            next_process: Process = self.waiting[0]
            self._waiting = self._waiting[1:]
            stall_time = next_process.arrival_time
            next_process.arrival_time = 0
            self.time += stall_time
            self.add_runnable(next_process)

    def add_runnable(self, process: Process) -> None:
        """
        Virtual Method
        Adds a process to the runnable queue
        :param process: The process to insert
        """
        raise NotImplementedError

    @property
    def is_done(self) -> bool:
        """
        :return: True if the scheduler is done running processes
        """
        return len(self.runnable) == 0 and len(self.waiting) == 0

    @property
    def done_processes(self) -> list:
        """
        :return: the list of done processes
        """
        return self._done_processes

    @property
    def runnable(self) -> list:
        """
        :return: the list of runnable processes
        """
        return self._runnable

    @runnable.setter
    def runnable(self, value):
        """
        Setter for the runnable list
        :param value: the new list to set
        """
        self._runnable = value

    @property
    def waiting(self) -> list:
        """
        :return: the list of __waiting processes
        """
        return self._waiting

    @property
    def time(self) -> int:
        """
        :return: the current time of the scheduler
        """
        return self._time

    @time.setter
    def time(self, value):
        """
        Sets the time of the scheduler
        :param value:
        """
        self._time = value

    @property
    def verbose(self) -> int:
        """
        :return: the verbose setting of the scheduler
        """
        return self._verbose

    @property
    def curr_process(self) -> Process:
        """
        :return: the current process that is running
        """
        return self._curr_process

    @property
    def step_time_ran(self) -> int:
        """
        :return: the amount of time ran in the last step
        """
        return self._step_time_ran

    def register_step_listener(self, func) -> None:
        """
        Adds a function to the step end listeners
        :param func: The function to add, takes two params
                     func(process, scheduler)
        """
        self._step_end_listeners.append(func)

    def _on_step_end(self) -> None:
        """
        Calls all event listeners for the end of a step
        """
        if self.verbose <= 1:
            return
        for listener in self._step_end_listeners:
            listener(self._curr_process, self)

    def register_process_done_listener(self, func) -> None:
        """
        Adds a function to the process done listeners
        :param func: The function to add, takes two params
                     func(process, scheduler)
        """
        self._process_done_listeners.append(func)

    def _on_process_done(self) -> None:
        """
        Calls all event listeners for the end of a process
        """
        # Save process to done list
        self._done_processes.append(self.curr_process)

        # Call all listeners
        if self.verbose <= 0:
            return
        for listener in self._process_done_listeners:
            listener(self._curr_process, self)

    def register_process_arrive_listener(self, func) -> None:
        """
        Adds a function to the process arrive listeners
        :param func: The function to add, takes two params
                     func(process, scheduler)
        """
        self._process_arrive_listeners.append(func)

    def _on_process_arrive(self) -> None:
        """
        Calls all event listeners for the arrival of a process
        """
        if self.verbose <= 1:
            return
        for listener in self._process_arrive_listeners:
            listener(self._curr_process, self)

    @verbose.setter
    def verbose(self, value):
        """
        Sets the value of the verbose attribute
        :param value: The new value
        """
        self._verbose = value


class FIFOScheduler(Scheduler):
    """
    Runs a FIFO (FCFS) process scheduling algorithm
    """

    def run(self) -> dict:
        """
        Runs the scheduling algorithm until all processes
        are finished.
        :return: a dictionary of summary statistics
        """
        super().run()
        self.stats['title'] = 'FIFO'
        return self.stats

    def step(self) -> bool:
        """
        Runs a single step of the scheduling algorithm
        """
        self._curr_process = self.get_next_process()
        ex_time = self._curr_process.ex_time
        self._step_time_ran, time_leftover = self._curr_process.run(ex_time)
        assert time_leftover == 0, "FIFO Should not interrupt running processes"

        # Print Running Data
        self._on_step_end()
        self._on_process_done()

        self.time += self.step_time_ran

        # Process waiting time
        for process in self.runnable:
            process.wait(self.step_time_ran)

        # Process waiting processes
        for process in self.waiting:
            if process.wait_arrival(self.step_time_ran):
                self.add_runnable(process)
                self._waiting = self._waiting[1:]

        return self.is_done

    def get_next_process(self) -> Process:
        """
        Gets the next process to run at the current time step
        The next process is the one at the front (ind = 0) of the waiting
        queue
        :return: The next process to be run, or None if one does not exist
        """
        super().get_next_process()
        curr_process = self.runnable[0]
        self.runnable = self.runnable[1:]
        return curr_process

    def add_runnable(self, process: Process) -> None:
        """
        Adds a process to the runnable queue
        :param process: The process to insert
        """
        self.runnable.append(process)


class SJFScheduler(Scheduler):
    """
    Runs the Shortest Job First (SJF) process scheduling algorithm
    """

    def __init__(self, processes: list, verbose: int = 1):
        """
        Initializes a new SJF Scheduler.
        :param processes: A list of processes to run
        :param verbose: The verbose setting for simulations
            0 = silent mode - Don't print anything
            1 = done mode = only print info about a process when it is done
            2 = print process done info and info about each simulation step
        """
        super().__init__(processes, verbose)
        self.runnable.sort()

    def run(self) -> dict:
        """
        Runs the scheduling algorithm until all processes
        are finished.
        :return: a dictionary of summary statistics
        """
        super().run()
        self.stats['title'] = 'SJF'
        return self.stats

    def step(self) -> bool:
        """
        Runs a single step of the scheduling algorithm
        :return: true if the scheduler is done
        """
        self._curr_process = self.get_next_process()
        ex_time = self._curr_process.ex_time
        self._step_time_ran, time_leftover = self._curr_process.run(ex_time)
        assert time_leftover == 0, "SJF Should not interrupt running processes"

        # Print Running Data
        self._on_step_end()
        self._on_process_done()

        self.time += self._step_time_ran

        # Process waiting time
        for process in self.runnable:
            process.wait(self._step_time_ran)

        # Process waiting processes
        for process in self.waiting:
            if process.wait_arrival(self._step_time_ran):
                self.add_runnable(process)
                self._waiting = self._waiting[1:]

        return self.is_done

    def get_next_process(self) -> Process:
        """
        Gets the next process to run at the current time step
        :return: The next process to be run
        """
        super().get_next_process()
        curr_process = self.runnable[0]
        self.runnable = self.runnable[1:]
        return curr_process

    def add_runnable(self, process: Process) -> None:
        """
        Adds a process to the runnable queue
        :param process: The process to insert
        """
        bisect.insort(self.runnable, process)


class RoundRobinScheduler(Scheduler):
    """
    Runs a Round Robin process scheduling algorithm
    """

    def __init__(self, processes: list, verbose: int = 1, time_slice: int = 1):
        """
        Initializes a new SJF Scheduler.
        :param processes: A list of processes to run
        :param verbose: The verbose setting for simulations
            0 = silent mode - Don't print anything
            1 = done mode = only print info about a process when it is done
            2 = print process done info and info about each simulation step
        """
        assert time_slice > 0, "Round Robin time slice must be positive"
        super().__init__(processes, verbose)
        self._time_slice = time_slice

    def run(self) -> dict:
        """
        Runs the scheduling algorithm until all processes
        are finished.
        :return: a dictionary of summary statistics
        """
        super().run()
        self.stats['title'] = f'R.R. ({self.time_slice})'
        self.stats['time_slice'] = self.time_slice
        return self.stats

    def step(self) -> bool:
        """
        Runs a single step of the scheduling algorithm
        :return: true if the scheduler is done
        """
        self._curr_process = self.get_next_process()
        ex_time = self.time_slice
        self._step_time_ran, time_leftover = self._curr_process.run(ex_time)

        # Print Running Data
        self._on_step_end()

        # Process waiting time
        for process in self.runnable:
            process.wait(self._step_time_ran)

        # Process waiting processes
        for process in self.waiting:
            if process.wait_arrival(self._step_time_ran):
                self.add_runnable(process)
                self._waiting = self._waiting[1:]

        # If process isn't done, requeue it
        if self.curr_process.is_done:
            self._on_process_done()
        else:
            self.add_runnable(self.curr_process)

        self.time += self._step_time_ran
        return self.is_done

    def get_next_process(self) -> Process:
        """
        Gets the next process to run at the current time step
        :return: The next process to be run
        """
        super().get_next_process()
        curr_process = self.runnable[0]
        self.runnable = self.runnable[1:]
        return curr_process

    def add_runnable(self, process: Process) -> None:
        """
        Adds a process to the runnable queue
        :param process: The process to insert
        """
        self.runnable.append(process)

    @property
    def time_slice(self):
        """
        :return: the time slice of the scheduler
        """
        return self._time_slice


class SRTFScheduler(Scheduler):
    """
    Runs the Shortest Remaining Time First (SRTF) process scheduling algorithm
    """

    def __init__(self, processes: list, verbose: int = 1):
        """
        Initializes a new SRTF Scheduler.
        :param processes: A list of processes to run
        :param verbose: The verbose setting for simulations
            0 = silent mode - Don't print anything
            1 = done mode = only print info about a process when it is done
            2 = print process done info and info about each simulation step
        """
        super().__init__(processes, verbose)
        self.runnable.sort()

    def run(self) -> dict:
        """
        Runs the scheduling algorithm until all processes
        are finished.
        :return: a dictionary of summary statistics
        """
        super().run()
        self.stats['title'] = 'SRTF'
        return self.stats

    def step(self) -> bool:
        """
        Runs a single step of the scheduling algorithm
        :return: true if the scheduler is done
        """
        self._curr_process = self.get_next_process()

        # Get execution time
        ex_time = self._curr_process.time_left
        if len(self.waiting) > 0:
            # Check if processes will be preempted
            first_waiting: Process = self.waiting[0]
            wait_comp_time = first_waiting.arrival_time + first_waiting.time_left
            if ex_time > wait_comp_time:
                # preemption will happen
                ex_time = first_waiting.arrival_time
            else:
                # no preemption will happen
                ex_time = self._curr_process.time_left

        self._step_time_ran, time_leftover = self._curr_process.run(ex_time)

        # Print Running Data
        self._on_step_end()

        # Process waiting time
        for process in self.runnable:
            process.wait(self._step_time_ran)

        # Process waiting processes
        for process in self.waiting:
            if process.wait_arrival(self._step_time_ran):
                self.add_runnable(process)
                self._waiting = self._waiting[1:]

        # If process isn't done, requeue it
        if self.curr_process.is_done:
            self._on_process_done()
        else:
            self.add_runnable(self.curr_process)

        self.time += self._step_time_ran
        return self.is_done

    def get_next_process(self) -> Process:
        """
        Gets the next process to run at the current time step
        :return: The next process to be run
        """
        super().get_next_process()
        curr_process = self.runnable[0]
        self.runnable = self.runnable[1:]
        return curr_process

    def add_runnable(self, process: Process) -> None:
        """
        Adds a process to the runnable queue
        :param process: The process to insert
        """
        bisect.insort(self.runnable, process)

