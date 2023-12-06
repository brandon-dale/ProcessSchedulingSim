
class Process:
    """ Container for the data of a single process """

    def __init__(self,
                 id: str,
                 ex_time: int,
                 arrival_time: int = 0):
        """
        Constructs a new Process object.
        :param id: A unique ID for the process
        :param ex_time: The total execution time that the process needs
        :param arrival_time: The time step where the process arrives
                             during execution
        """
        # Process Attributes
        self.__id = id  # unique process id
        self.__ex_time = ex_time  # total execution time required
        self.__arrival_time = arrival_time  # process arrival time
        # Simulation Specific Attributes
        self.__processed_time = 0  # amount of time processed from ex_time
        self.__comp_time = 0  # total time for process to complete
        self.__wait_time = 0  # total time process waited

    def run(self, running_time: int = 1) -> (int, int):
        """
        Run the process for the given time
        :param running_time: Amount of time to run - default to 1
        :return: A tuple containing (time_ran, time_leftover)
        """
        assert running_time > 0, "Process running_time must be > 0"
        time_ran = min(self.time_left, running_time)
        self.__processed_time += time_ran
        time_leftover = running_time - time_ran
        self.__comp_time += time_ran
        return time_ran, time_leftover

    def wait(self, waiting_time: int) -> None:
        """
        Process a waiting time for a runnable process
        Adds the waiting_time to the process wait_time
        :param waiting_time: the amount of time to wait
        """
        assert waiting_time >= 0, "Cannot wait for negative time"
        self.__wait_time += waiting_time
        self.__comp_time += waiting_time

    def wait_arrival(self, waiting_time: int) -> bool:
        """
        Processes a waiting time for a waiting processes that
        has not arrived.
        If waiting_time > arrival_time, then process goes into a
        waiting pattern.
        :param waiting_time: the time to wait
        :return: true if the process became runnable, else false
        """
        assert waiting_time >= 0, "Cannot wait for negative time"
        arrival_wait_time = min(self.arrival_time, waiting_time)
        self.arrival_time -= arrival_wait_time
        waiting_time -= arrival_wait_time
        self.wait(waiting_time)
        return self.arrival_time == 0

    @property
    def is_done(self) -> bool:
        """
        :return: true if process is done executing
        """
        return self.__processed_time >= self.__ex_time

    @property
    def time_left(self) -> int:
        """
        :return: The amout of execution time the process has left
        """
        return self.__ex_time - self.__processed_time

    @property
    def completion_time(self) -> int:
        """
        :return: The total completion time for a finished process
        """
        assert self.is_done, "cannot get completion time for ongoing process"
        return self.__comp_time

    @property
    def id(self) -> str:
        """
        :return: The processes id
        """
        return self.__id

    @property
    def ex_time(self) -> int:
        """
        :return: The execution time for the process
        """
        return self.__ex_time

    @property
    def wait_time(self) -> int:
        """
        :return: The current wait time
        """
        return self.__wait_time

    @property
    def arrival_time(self) -> int:
        """
        :return: The arrival time
        """
        return self.__arrival_time

    @property
    def time_run(self) -> int:
        """
        :return: the amount of time that the process has run
        """
        return self.__processed_time

    @completion_time.setter
    def completion_time(self, value: int) -> None:
        """
        Setter for self.__comp_time
        :param value: the value to set
        """
        self.__comp_time = value

    @arrival_time.setter
    def arrival_time(self, value: int) -> None:
        """
        Setter for self.__arrival_time
        :param value: the value to set
        """
        self.__arrival_time = value

    @staticmethod
    def read_processes(path: str) -> list:
        """
        Reads in a list of Processes from a given .txt file, specified
        by the path parameter
        Each line should contain the data for a single process in the form:
            pid execution_time arrival_time (optional)
        Where each piece of data is separated by at least one space.
        :param path: A relative file path which contains valid input
                     for a list of processes
        :return: A list of processes
        """
        processes = []
        delimiter = ' '
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                line_list = line.split(delimiter)
                pid: str = line_list[0]
                ex_time: int = int(line_list[1])
                arrival_time: int = int(line_list[2]) if len(line_list) >= 3 else 0
                processes.append(Process(pid, ex_time, arrival_time))

        return processes

    def __str__(self):
        """
        Convert the process into a formatted string
        """
        res: str = f"Process {self.id}\n"
        res += f"\tEx. Time:  {self.ex_time}\n"
        res += f"\tTime Run:  {self.time_run}\n"
        res += f"\tWait Time: {self.wait_time}\n"
        if self.is_done:
            res += f"\tComp Time: {self.completion_time}\n"
        return res

    def __repr__(self):
        return f"Process({self.id}, {self.ex_time}, {self.arrival_time})"

    def __lt__(self, other):
        if self.arrival_time == other.arrival_time:
            return self.ex_time < other.ex_time
        return self.arrival_time < other.arrival_time
