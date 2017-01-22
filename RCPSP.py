def main():
    new_or_rerun = input("Welcome to RCPSP-Lab.  Please type 'N' to enter " 
    "a new dataset or 'E' to work with an existing dataset.  Type 'Q' to quit: ")

    if new_or_rerun == "N":
        project_number = openfile()
    elif new_or_rerun == "E":
        project_number = input("\nPlease type the project number: ")
        pull_inputs(project_number)
    elif new_or_rerun == "Q":
        print("\nExiting RCPSP-Lab.\n")
    else:
        print("\nSorry, your input was not recognized.\n")
        main()

    #project_number = openfile()
    # to get raw printout, print(repr(<string>))

def openfile():
    file = input("Please type the filename (including path) for the project: ")
    f = open(file,"r")
    raw_data = f.read()

    if raw_data[0].isnumeric() and raw_data[raw_data.find("\n") + 1].isnumeric():
        print("Converting RCP file to appropriate format...")
        convert_rcp(raw_data)
        project_number = name_project()
        return(project_number)
    elif (raw_data[0:9] == "Resources" and raw_data[find_nth(raw_data,"\n",4) +
            1:find_nth(raw_data,"\n",4) + 6] == "Tasks"):
        print("File is in appropriate format!")
        csv_data = import_csv(file)
        project_number = name_project()
        make_dictionary(csv_data,project_number)
        pull_inputs(project_number)
        return(project_number)
    else:
        print("Error - the selected file appears to be in the wrong format.")

def find_nth(haystack, needle, n):
    start = haystack.find(needle)

    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1

    return start

def convert_rcp(raw_data):
    import re
    import csv
    raw_data = re.sub(r' {1,}', ',',raw_data)
    num_resources = int(raw_data[find_nth(raw_data,",",1) + 1:
        find_nth(raw_data,",",2)])
    resource_string = ""

    for i in range(1,num_resources + 1):
        resource_string = resource_string + "R" + str(i) + ","

    raw_data = "Resources,\n" + resource_string + raw_data[raw_data.find("\n"):
        find_nth(raw_data,"\n",2)] + "\n\nTasks,\nDuration," + resource_string \
        + "NumSuccessors,Successors,\n" + raw_data[find_nth(raw_data,"\n",2) + 1:]
    csv_data = list(csv.reader(raw_data.split("\n"), delimiter =","))
    make_dictionary(csv_data)

def import_csv(file):
    import csv
    csv_data = list(csv.reader(open(file, newline =""),delimiter=",", quotechar="|"))
    return csv_data

def name_project():
    import _mysql
    import MySQLdb
    
    project_name = input("Please type a unique name for this project:")

    db = MySQLdb.connect("localhost", "root", "stinkydogfarts", 
        "scheduling_problems")
    c = db.cursor()
    current_results = c.execute("""SELECT project_name FROM projects WHERE 
        project_name = (%s)""", ([project_name]))
    if current_results > 0:
        print("Sorry, this name has been used before.  Please try again.")
        name_project()
    else:
        c.execute("""INSERT INTO projects (project_name)
                        VALUES(%s)""",
                        ([project_name]))
        db.commit()
        c.execute("""SELECT project_id FROM projects WHERE 
        project_name = (%s)""", ([project_name]))
        project_number = int(c.fetchone()[0])
        return(project_number)

def make_dictionary(csv_data, project_number):
    import csv

    resource_list = strip_blanks([val for sublist in csv_data[1:2] for val in sublist])
    resources = strip_blanks([val for sublist in csv_data[2:3] for val in sublist])
    resource_dictionary = {}

    if len(resource_list) != len(resources):
        print("There is a problem with the resource list.  Please verify input data and try again.")
        quit()
    else:
        for i in range(1,len(resource_list)+1):
            resource_dictionary[i] = {}
            resource_dictionary[i]["resource_name"] = resource_list[i-1]
            resource_dictionary[i]["capacity"] = resources[i-1]

    resources_fill(resource_dictionary,project_number)

    task_headers = strip_blanks([val for sublist in csv_data[5:6] for val in sublist])
    task_data = csv_data[6:]
    task_dictionary = {}

    for i in range(0,len(task_data)):
        mini_task_data = task_data[i]
        mini_task_data = strip_blanks(mini_task_data)

        if len(mini_task_data) > len(task_headers)-1:
            mini_task_data[len(task_headers)-1] = mini_task_data[len(task_headers)-1:]
        elif len(mini_task_data) == len(task_headers)-1:
            mini_task_data.append([''])
        else:
            Print("There is a problem with the task data.  Please verify input data and try again.")
            quit()

        mini_task_data[len(task_headers):] = ''
        mini_task_data = strip_blanks(mini_task_data)
        task_dictionary[i+1] = {}
        task_dictionary[i+1] = dict(zip(task_headers,mini_task_data))
        for k, v in resource_dictionary.items():
            for kk, vv in v.items():
                if vv == task_dictionary[i+1]["Resource"]:
                    task_dictionary[i+1]["Resource"] = k

    tasks_fill(task_dictionary,project_number)

def strip_blanks(input_array):
    output_array = [i for i in input_array if i !=""]
    return(output_array)

def tasks_fill(task_dictionary,project_number):
    import _mysql
    import MySQLdb

    db = MySQLdb.connect("localhost", "root", "stinkydogfarts", 
        "scheduling_problems")
    c = db.cursor()
    for i in range(1,len(task_dictionary)+1):
        c.execute("""INSERT INTO jobs (project_num, job_number, job_name, 
            duration, resource_number, resource_load, successors)
                    VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                    (project_number, task_dictionary[i]["Task_Num"], 
                        task_dictionary[i]["Task_Name"], 
                        task_dictionary[i]["Duration"], 
                        task_dictionary[i]["Resource"], 
                        task_dictionary[i]["Load"], 
                        str(task_dictionary[i]["Successors"])))
    db.commit()
    #c.execute("""SELECT * FROM jobs""")
    #storage = c.fetchall()
    #print(storage)

def resources_fill(resource_dictionary,project_number):
    import _mysql
    import MySQLdb

    db = MySQLdb.connect("localhost", "root", "stinkydogfarts", 
        "scheduling_problems")
    c = db.cursor()
    for i in range(1,len(resource_dictionary)+1):
        c.execute("""INSERT INTO resources (project_num, resource_number, 
            resource_name, capacity)
                    VALUES(%s, %s, %s, %s)""",
                    (project_number, i, 
                        resource_dictionary[i]["resource_name"], 
                        resource_dictionary[i]["capacity"]))
    db.commit()
    #c.execute("""SELECT * FROM resources""")
    #storage = c.fetchall()
    #print(storage)

def pull_inputs(project_number):
    import _mysql
    import MySQLdb
    import MySQLdb.cursors

    db = MySQLdb.connect("localhost", "root", "stinkydogfarts", 
        "scheduling_problems", cursorclass=MySQLdb.cursors.DictCursor)
    c = db.cursor()
    c.execute("""SELECT * FROM projects WHERE 
        project_id = (%s)""", ([project_number]))
    project_data = c.fetchone()

    c.execute("""SELECT * FROM jobs WHERE project_num = (%s)""", 
        ([project_number]))
    job_data = c.fetchall()

    c.execute("""SELECT * FROM resources WHERE project_num = (%s)""", 
        ([project_number]))
    resource_data = c.fetchall()

    conditions_table(project_number,job_data)

def conditions_table(project_number,job_data):
    import json

    task_pairs = []

    for i in range(0,len(job_data)):
        predecessor = job_data[i]["job_number"]
        successors = json.loads(str(job_data[i]["successors"]).replace("'",'"'))
        for i in range(0,len(successors)):
            if len(successors[i]) == 0:
                successors[i] = 0
            task_pairs.append((predecessor,int(successors[i])))
    schedule_tasks(project_number,job_data,task_pairs)

def schedule_tasks(project_number,job_data,task_pairs):
    scheduled_tasks = []
    to_schedule = []
    task_durations = []

    # Create a list of tasks and lengths
    for i in range(0,len(job_data)):
        task = job_data[i]["job_number"]
        duration = job_data[i]["duration"]
        task_durations.append((task,duration))

    # Schedule any tasks that do not have predecessors - need to fix to deal with tasks with 0 as predecessor
    for k, v in task_pairs:
        if k not in [i[1] for i in task_pairs]:
            to_schedule.append(k)

    to_schedule = set(to_schedule)
    schedule = {}

    for i in to_schedule:
        schedule[i] = {}
        schedule[i]["start_time"] = 0
        for task, duration in task_durations:
            if task == i:
                task_length = duration

        schedule[i]["end_time"] = schedule[i]["start_time"] + task_length

    # Schedule tasks whose predecessors have all been scheduled.
    limited_task_pairs = task_pairs

    while limited_task_pairs:
        for i in to_schedule:
            limited_task_pairs = list(filter(lambda k : k[0] != i, limited_task_pairs))
        #    for k in reversed(task_pairs):
        #        print(k[0])
        #        if k[0] == i:
        #            task_pairs.remove(k)

        to_schedule = []

        for k, v in limited_task_pairs:
            if k not in [i[1] for i in limited_task_pairs]:
                to_schedule.append(k)

        to_schedule = set(to_schedule)

        for i in to_schedule:
            schedule[i] = {}
            predecessors = []
            for k, v in task_pairs:
                if v == i:
                    predecessors.append(schedule[k]["end_time"])
            schedule[i]["start_time"] = max(predecessors)
            for task, duration in task_durations:
                if task == i:
                    task_length = duration

            schedule[i]["end_time"] = schedule[i]["start_time"] + task_length

    graph_schedule(project_number,job_data,schedule)

def graph_schedule(project_number,job_data,schedule):
    from bokeh.plotting import figure, output_file, show, reset_output
    from bokeh.models import Range1d, HoverTool, ColumnDataSource
    import pandas as pd

    output_file("schedule.html")
    p = figure(plot_width = 800, plot_height = 600, 
        title = "Schedule for Project " + str(project_number), 
        tools = 'hover')
    y = []
    right = []
    left = []
    task_name = []
    max_time = 0

    jobs = []

    #for i in range(0, len(job_data)):
    #    jobs.append(job_data[i]["job_number"])

    #print(jobs)

    #details = pd.DataFrame(job_data, index = jobs)
    #print(details)
    #pd.DataFrame.from_dict(job_data, orient='columns', dtype=None)

    for i in schedule:
        y.append(i)
        left.append(int(schedule[i]["start_time"]))
        right.append(int(schedule[i]["end_time"]))
        task_name.append("name test")
        max_task = i

        if int(schedule[i]["end_time"]) > max_time:
            max_time = int(schedule[i]["end_time"])

    p.hbar(y, .8, right, left, color ="#B3DE69")
    p.y_range = Range1d(max_task + .5,.5)
    p.x_range = Range1d(0, max_time)
    p.xaxis.axis_label = "Time (periods)"
    p.yaxis.axis_label = "Task"
    p.ygrid.grid_line_color = None

    # Add task descriptions in hovertool.
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ("Task Number", '@y'),
        #("Task Name", '@task_name'),
        ("Start Time", '@left'),
        ("End Time", '@right')
    ]
    show(p)
    reset_output()