def main():
    new_or_rerun = input("Welcome to RCPSP-Lab.  Please type 'N' to enter " 
    "a new dataset or 'E' to work with an existing dataset.  Type 'Q' to quit: ")

    if new_or_rerun == "N":
        project_number = openfile()
    elif new_or_rerun == "E":
        project_number = input("\nPlease type the project number: ")
        selected_rule = select_rule()
        pull_inputs(project_number, selected_rule)
    elif new_or_rerun == "Q":
        print("\nExiting RCPSP-Lab.\n")
    else:
        print("\nSorry, your input was not recognized.\n")
        main()

    #project_number = openfile()
    # to get raw printout, print(repr(<string>))


def autorun(selected_rule):
    # Add new project to file
    # for i in range(2,49):
    #     for j in range(1, 11):
    #         file = "/home/squigglily/Documents/School Stuff/Grad School/Independent_Study/RCP/J30" + str(i) + "_" + str(j) + ".RCP"
    #         project = "J30" + str(i) + "_" + str(j)
    #         # Add data to database.
    #         if selected_rule == 0:
    #             project_number = auto_open(file, selected_rule, project)
    #         else:
    #             project_number = project_number
    #             selected_rule = selected_rule
    #             pull_inputs(project_number, selected_rule, project)

    # Run selected rule on all "real" data available
    for i in range(43,523):
        project_number = i
        selected_rule = selected_rule
        pull_inputs(project_number, selected_rule)        


def auto_open(file, selected_rule, project):
    import sys

    f = open(file,"r")
    raw_data = f.read()

    if raw_data[0].isnumeric() and raw_data[raw_data.find("\n") + 1].isnumeric():
        print("Converting RCP file to appropriate format...")
        csv_data = convert_rcp(raw_data)
    elif (raw_data[0:9] == "Resources" and raw_data[find_nth(raw_data,"\n",4) +
            1:find_nth(raw_data,"\n",4) + 6] == "Tasks"):
        print("File is in appropriate format!")
        csv_data = import_csv(file)
    else:
        print("Error - the selected file appears to be in the wrong format.")
        sys.exit()

    project_number = autoname_project(project)
    make_dictionary(csv_data,project_number)
    selected_rule = selected_rule
    pull_inputs(project_number, selected_rule)
    return(project_number)

def autoname_project(project):
    import _mysql
    import MySQLdb
    
    project_name = project

    db = MySQLdb.connect("localhost", "root", "stinkydogfarts", 
        "scheduling_problems")
    c = db.cursor()
    current_results = c.execute("""SELECT project_name FROM projects WHERE 
        project_name = (%s)""", ([project_name]))
    if current_results > 0:
        print("Sorry, this name has been used before.  Please try again.")
        return(project_name)
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

def openfile():
    import sys

    file = input("Please type the filename (including path) for the project: ")
    f = open(file,"r")
    raw_data = f.read()

    if raw_data[0].isnumeric() and raw_data[raw_data.find("\n") + 1].isnumeric():
        print("Converting RCP file to appropriate format...")
        csv_data = convert_rcp(raw_data)
    elif (raw_data[0:9] == "Resources" and raw_data[find_nth(raw_data,"\n",4) +
            1:find_nth(raw_data,"\n",4) + 6] == "Tasks"):
        print("File is in appropriate format!")
        csv_data = import_csv(file)
    else:
        print("Error - the selected file appears to be in the wrong format.")
        sys.exit()

    project_number = name_project()
    make_dictionary(csv_data,project_number)
    selected_rule = select_rule()
    pull_inputs(project_number, selected_rule)
    return(project_number)

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
    for i in range(6,len(csv_data)):
        sublist = csv_data[i]
        resources = sublist[1:num_resources + 1]
        resource = '0'
        task_num = i - 5
        usage = 0

        for j in range(0,len(resources)):
            if int(resources[j]) > 0:
                resource = csv_data[5][j + 1]
                usage = int(resources[j])

        updated_row = [task_num, task_num, sublist[0], resource, usage] + sublist[2 + len(resources):-1]

        csv_data[i] = updated_row
    csv_data[5] = ['Task_Num', 'Task_Name', 'Duration', 'Resource', 'Load', 'Successors']
    return(csv_data)

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
        return(project_name)
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

def pull_inputs(project_number, selected_rule):
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

    conditions_table(project_number,job_data, resource_data, selected_rule)

def conditions_table(project_number,job_data,resource_data, selected_rule):
    import json

    task_pairs = []

    for i in range(0,len(job_data)):
        predecessor = job_data[i]["job_number"]
        successors = json.loads(str(job_data[i]["successors"]).replace("'",'"'))
        for i in range(0,len(successors)):
            if len(successors[i]) == 0:
                successors[i] = 0
            task_pairs.append((predecessor,int(successors[i])))

    # Remove task pairs for tasks with no predecessors.
    task_pairs = list(filter(lambda k : k[0] != 0, task_pairs))

    schedule_in_time(project_number,job_data,task_pairs, resource_data, selected_rule)

def schedule_fill(project_number, job_data, schedule, selected_rule):
    import _mysql
    import MySQLdb

    db = MySQLdb.connect("localhost", "root", "stinkydogfarts", 
        "scheduling_problems")
    c = db.cursor()
    c.execute("""INSERT INTO schedules (project_num, trial_description)
                    VALUES(%s, %s)""",
                    ([project_number, selected_rule]))
    db.commit()
    c.execute("""SELECT MAX(id) AS article FROM schedules WHERE 
    project_num = (%s)""", ([project_number]))
    trials = c.fetchall()
    trial_number = int(trials[0][0])

    for i in range(1,len(schedule)+1):
        c.execute("""INSERT INTO schedule_details (project_num, job_number, 
            start_time, end_time, trial_number)
                    VALUES(%s, %s, %s, %s, %s)""",
                    (project_number, i, 
                        schedule[i]["start_time"], 
                        schedule[i]["end_time"], 
                        trial_number))
    db.commit()

def graph_schedule(project_number,job_data,schedule):
    from bokeh.plotting import figure, output_file, show, reset_output
    from bokeh.models import Range1d, HoverTool, ColumnDataSource
    from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
    from bokeh.io import vform
    from bokeh.layouts import widgetbox, column, row
    import pandas as pd

    data = job_data

    for i in range(0,len(data)):
        for j in range(1,len(schedule) + 1):
            if j == data[i]["job_number"]:
                data[i]["end_time"] = schedule[j]["end_time"]
                data[i]["start_time"] = schedule[j]["start_time"]

    job_number = []
    job_name = []
    start_time = []
    end_time = []
    resource_number = []
    resource_load = []
    successors = []

    for i in range(0,len(data)):
        job_number.append(data[i]["job_number"])
        job_name.append(data[i]["job_name"])
        start_time.append(data[i]["start_time"])
        end_time.append(data[i]["end_time"])
        resource_number.append(data[i]["resource_number"])
        resource_load.append(data[i]["resource_load"])
        successors.append(data[i]["successors"])


    output_file("schedule.html")

    data = dict(
            task_number = job_number, 
            task_name = job_name,
            start = start_time,
            end = end_time,
            resource = resource_number,
            load = resource_load,
            next = successors,
        )

    source = ColumnDataSource(data)
    columns = [
            TableColumn(field = "task_number", title = "Task Number"),
            TableColumn(field = "task_name", title = "Task Name"),
            TableColumn(field = "start", title = "Start Time"),
            TableColumn(field = "end", title = "End Time"),
            TableColumn(field = "resource", title = "Resource #"),
            TableColumn(field = "load", title = "Resource Load"),
            TableColumn(field = "next", title = "Successors")
        ]
    
    data_table = DataTable(source = source, columns = columns, 
        width = 600, height = 850, fit_columns = True, row_headers = False,
        selectable = True)

    p = figure(plot_width = 800, plot_height = 600, 
        title = "Schedule for Project " + str(project_number), 
        tools = 'tap,hover')

    max_task = max(data["task_number"])
    max_time = max(data["end"])

    p.hbar(data["task_number"], .8, data["end"], data["start"], color ="#B3DE69")
    p.y_range = Range1d(max_task + .5,.5)
    p.x_range = Range1d(0, max_time)
    p.xaxis.axis_label = "Time (periods)"
    p.yaxis.axis_label = "Task"
    p.ygrid.grid_line_color = None

    # Add task descriptions in hovertool.
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ("Task Number", '@y'),
    ]
    show(row(p,widgetbox(data_table)))
    reset_output()

def check_constraints(i,project_number,job_data, t,schedule,to_schedule, resource_data, selected_rule, task_pairs):
    # Check to see if there is enough capacity to perform the task.
    task_number = i
    desired_start = t
    potential_conflicts = []
    conflict_details = {}
    actual_conflicts = []
    conflicting_tasks = [task_number]
    schedule_order = []
    max_load = 0

    for i in range(0,len(job_data)):
        if int(job_data[i]["job_number"]) == task_number:
            duration = job_data[i]["duration"]

    # Add potential conflicts that have already been scheduled.
    for i in schedule:
        if schedule[i]["start_time"] <= desired_start + duration and \
                schedule[i]["end_time"] > desired_start:
            potential_conflicts.append(i)
    
    # Check to see if there is capacity for the task at the desired start time, based on previously scheduled tasks.
    for j in range(0,len(job_data)):
        if int(job_data[j]["job_number"]) == task_number:
            start_load = job_data[j]["resource_load"]
            resource_number = job_data[j]["resource_number"]

    for i in potential_conflicts:
        for j in range(0, len(job_data)):
            if int(job_data[j]["job_number"]) == i and job_data[j]["resource_number"] == resource_number:
                start_load = start_load + job_data[j]["resource_load"]

    for i in range(0,len(resource_data)):
        if resource_data[i]["resource_number"] == resource_number:
            max_load = resource_data[i]["capacity"]

    if start_load > max_load:
        return(99999)

    else:

        # Add potential conflicts we are trying to schedule now.
        for i in to_schedule:
            potential_conflicts.append(i)

        if len(potential_conflicts) <= 1:
            return(task_number)
        else:
            for i in range(0,len(job_data)):
                if int(job_data[i]["job_number"]) == task_number:
                    conflict_details[task_number] = {}
                    conflict_details[task_number]["resource_number"] = job_data[i]["resource_number"]
                    conflict_details[task_number]["resource_load"] = job_data[i]["resource_load"]
                    conflict_details[task_number]["start_time"] = desired_start
                    conflict_details[task_number]["duration"] = duration
                elif int(job_data[i]["job_number"]) in to_schedule:
                    conflict_details[job_data[i]["job_number"]] = {}
                    conflict_details[job_data[i]["job_number"]]["resource_number"] = job_data[i]["resource_number"]
                    conflict_details[job_data[i]["job_number"]]["resource_load"] = job_data[i]["resource_load"]
                    conflict_details[job_data[i]["job_number"]]["start_time"] = desired_start
                    conflict_details[job_data[i]["job_number"]]["duration"] = job_data[i]["duration"]
                elif int(job_data[i]["job_number"]) in potential_conflicts:
                    conflict_details[job_data[i]["job_number"]] = {}
                    conflict_details[job_data[i]["job_number"]]["resource_number"] = job_data[i]["resource_number"]
                    conflict_details[job_data[i]["job_number"]]["resource_load"] = job_data[i]["resource_load"]
                    conflict_details[job_data[i]["job_number"]]["start_time"] = schedule[job_data[i]["job_number"]]["start_time"]
                    conflict_details[job_data[i]["job_number"]]["duration"] = job_data[i]["duration"]
            for time in range(desired_start, desired_start + duration):
                total_load = conflict_details[task_number]["resource_load"]
                for i in potential_conflicts:
                    if conflict_details[i]["start_time"] <= time and conflict_details[i]["start_time"] + conflict_details[i]["duration"] > time:
                        if conflict_details[i]["resource_number"] == conflict_details[task_number]["resource_number"] and i != task_number:
                            total_load = total_load + conflict_details[i]["resource_load"]
                            conflicting_tasks.append(i)
                for i in range(0,len(resource_data)):
                    if resource_data[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
                        if total_load > resource_data[i]["capacity"]:
                            conflicting_tasks.append(task_number)
                            actual_conflicts = set(conflicting_tasks)

            schedule_next = prioritize_tasks(actual_conflicts, selected_rule, task_number, conflict_details, task_pairs, job_data, t, schedule)

            # Figure out if we can schedule even though not top priority.
            if schedule_next != task_number:
                schedule_priority = schedule_next
                schedule_order.append(schedule_priority)
                limited_conflict_details = dict(conflict_details)
                mod_load = []
                while schedule_priority != task_number:
                    limited_conflicts = actual_conflicts
                    if schedule_priority in limited_conflicts:
                        limited_conflicts.remove(schedule_priority)
                    del limited_conflict_details[schedule_priority]
                    schedule_priority = prioritize_tasks(limited_conflicts, selected_rule, task_number, limited_conflict_details, task_pairs, job_data, t, schedule)
                    schedule_order.append(schedule_priority)

                for i in range(0,len(resource_data)):
                    if resource_data[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
                        max_load = resource_data[i]["capacity"]

                for time in range(desired_start, desired_start + duration):
                    time_load = 0
                    for i in schedule_order:
                        if conflict_details[i]["start_time"] <= time and conflict_details[i]["start_time"] + conflict_details[i]["duration"] > time:
                            if conflict_details[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
                                time_load = time_load + conflict_details[i]["resource_load"]
                    mod_load.append(time_load)
                
                if all(i <= max_load for i in mod_load):
                        schedule_next = task_number

            return(schedule_next)

def prioritize_tasks(actual_conflicts, selected_rule, task_number, conflict_details, task_pairs, job_data, t, schedule):

    if selected_rule == 0:
        return(task_number)
    elif selected_rule == 1:
        priority = prioritize_by_number(task_number, actual_conflicts, selected_rule)
        return(priority)
    elif selected_rule == 2:
        priority = prioritize_by_demand(task_number, actual_conflicts, conflict_details, selected_rule)
        return(priority)
    elif selected_rule == 3:
        priority = prioritize_by_successors(task_number, actual_conflicts, conflict_details, task_pairs, selected_rule)
        return(priority)
    elif selected_rule == 4:
        priority = prioritize_by_finish_time(task_number, actual_conflicts, conflict_details, selected_rule)
        return(priority)
    elif selected_rule == 5:
        priority = prioritize_by_grpw(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule)
        return(priority)
    elif selected_rule == 6:
        priority = prioritize_by_grpw_star(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule)
        return(priority)
    elif selected_rule == 7:
        priority = prioritize_by_multi_pass(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule, t)
        return(priority)

def prioritize_by_number(task_number, actual_conflicts, selected_rule):
    # Prioritize tasks based on task number and nothing else.
    new_priorities = []
    if len(actual_conflicts) == 0:
        schedule_next = task_number
    else:
        prioritized = sorted(actual_conflicts)
        schedule_next = prioritized[0]

    for i in prioritized:
        new_priorities.append((i, i))

    prioritized = new_priorities

    if selected_rule > 6:
        return(prioritized)
    else:
        return(schedule_next)

def prioritize_by_demand(task_number, actual_conflicts, conflict_details, selected_rule):
    max_load = conflict_details[task_number]["resource_load"] * conflict_details[task_number]["duration"]
    schedule_next = task_number
    prioritized = [(task_number, conflict_details[task_number]["resource_load"] * conflict_details[task_number]["duration"])]

    for i in conflict_details:
        if i != task_number and conflict_details[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
            priority = conflict_details[i]["resource_load"] * conflict_details[i]["duration"]
            prioritized.append((i, priority))
            if conflict_details[i]["resource_load"] * conflict_details[i]["duration"] > max_load:
                max_load = conflict_details[i]["resource_load"] * conflict_details[i]["duration"]
                schedule_next = i
    
    prioritized = list(reversed(sorted(prioritized, key = lambda x: x[1])))
    
    if selected_rule > 6:
        return(prioritized)
    else:
        return(schedule_next)

def prioritize_by_successors(task_number, actual_conflicts, conflict_details, task_pairs, selected_rule):

    #This is screwed up and returning just one value

    for i in conflict_details:
        conflict_details[i]["successor_list"] = [i]
        for j in conflict_details[i]["successor_list"]:
            for k, v in task_pairs:
                if k == j:
                    conflict_details[i]["successor_list"].append(v)
        conflict_details[i]["successor_list"] = list(filter(lambda k : k != 0, conflict_details[i]["successor_list"]))
        conflict_details[i]["successor_list"] = set(conflict_details[i]["successor_list"])
    schedule_next = task_number
    num_successors = len(conflict_details[task_number]["successor_list"])
    prioritized = [(task_number, len(conflict_details[task_number]["successor_list"]))]
    for i in conflict_details:
        if i != task_number and conflict_details[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
            priority = len(conflict_details[i]["successor_list"])
            prioritized.append((i, priority))
            if len(conflict_details[i]["successor_list"]) > num_successors:
                schedule_next = i
                num_successors = len(conflict_details[i]["successor_list"])

    prioritized = list(reversed(sorted(prioritized, key = lambda x: x[1])))
    
    if selected_rule > 6:
        return(prioritized)
    else:
        return(schedule_next)

def prioritize_by_finish_time(task_number, actual_conflicts, conflict_details, selected_rule):
    max_time = conflict_details[task_number]["duration"]
    schedule_next = task_number
    prioritized = [(task_number, conflict_details[task_number]["duration"])]

    for i in conflict_details:
        if i != task_number and conflict_details[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
            priority = conflict_details[i]["duration"]
            prioritized.append((i, priority))
            if conflict_details[i]["duration"] > max_time:
                max_time = conflict_details[i]["duration"]
                schedule_next = i
    prioritized = list(reversed(sorted(prioritized, key = lambda x: x[1])))

    if selected_rule > 6:
        return(prioritized)
    else:
        return(schedule_next)

def prioritize_by_grpw(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule):
    prioritized = []

    for i in conflict_details:
        conflict_details[i]["successor_list"] = [i]
        for k, v in task_pairs:
            if k == i:
                conflict_details[i]["successor_list"].append(v)
        conflict_details[i]["successor_list"] = list(filter(lambda k : k != 0, conflict_details[i]["successor_list"]))
        conflict_details[i]["successor_list"] = set(conflict_details[i]["successor_list"])
        conflict_details[i]["rpw"] = 0
        for j in conflict_details[i]["successor_list"]:
            for k in range(0,len(job_data)):
                if job_data[k]["job_number"] == j:
                    conflict_details[i]["rpw"] = conflict_details[i]["rpw"] + job_data[k]["duration"]
    schedule_next = task_number
    grpw = conflict_details[task_number]["rpw"]
    prioritized.append((task_number, grpw))
    for i in conflict_details:
        if i != task_number and conflict_details[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
            priority = conflict_details[i]["rpw"]
            prioritized.append((i, priority))
            if conflict_details[i]["rpw"] > grpw:
                schedule_next = i
                grpw = conflict_details[i]["rpw"]
    
    prioritized = list(reversed(sorted(prioritized, key = lambda x: x[1])))

    if selected_rule > 6:
        return(prioritized)
    else:
        return(schedule_next)

def prioritize_by_grpw_star(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule):
    prioritized = []

    for i in conflict_details:
        conflict_details[i]["successor_list"] = [i]
        for j in conflict_details[i]["successor_list"]:
            for k, v in task_pairs:
                if k == j:
                    conflict_details[i]["successor_list"].append(v)
        conflict_details[i]["successor_list"] = list(filter(lambda k : k != 0, conflict_details[i]["successor_list"]))
        conflict_details[i]["successor_list"] = set(conflict_details[i]["successor_list"])
        conflict_details[i]["rpw"] = 0
        for j in conflict_details[i]["successor_list"]:
            for k in range(0,len(job_data)):
                if job_data[k]["job_number"] == j:
                    conflict_details[i]["rpw"] = conflict_details[i]["rpw"] + job_data[k]["duration"]
    schedule_next = task_number
    grpw = conflict_details[task_number]["rpw"]
    prioritized.append((task_number, grpw))
    for i in conflict_details:
        if i != task_number and conflict_details[i]["resource_number"] == conflict_details[task_number]["resource_number"]:
            priority = conflict_details[i]["rpw"]
            prioritized.append((i, priority))
            if conflict_details[i]["rpw"] > grpw:
                schedule_next = i
                grpw = conflict_details[i]["rpw"]
    
    prioritized = list(reversed(sorted(prioritized, key = lambda x: x[1])))

    if selected_rule > 6:
        return(prioritized)
    else:
        return(schedule_next)

def prioritize_by_multi_pass(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule, t):

    priority1 = prioritize_by_number(task_number, actual_conflicts, selected_rule)
    priority2 = prioritize_by_demand(task_number, actual_conflicts, conflict_details, selected_rule)
    priority3 = prioritize_by_successors(task_number, actual_conflicts, conflict_details, task_pairs, selected_rule)
    priority4 = prioritize_by_finish_time(task_number, actual_conflicts, conflict_details, selected_rule)
    priority5 = prioritize_by_grpw(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule)
    priority6 = prioritize_by_grpw_star(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule)

    lists = [priority1, priority2, priority3, priority4, priority5, priority6]

    for i in lists:
        for k, v in i:
            if k == task_number:
                location = i.index((k, v))
                while i[location][1] == i[location - 1][1]:
                    i[location - 1], i[location] = i[location], i[location - 1]

        schedule_details(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule, t, i)

def schedule_details(task_number, actual_conflicts, conflict_details, task_pairs, job_data, selected_rule, t, i):
    to_schedule = []

    for k, v in i:
        to_schedule.append(k)

    time = t

    print(task_number)
    print(actual_conflicts)
    print(to_schedule)
    print(conflict_details)
    #while to_schedule:


def select_rule():
    selected_rule = 0
    selected_rule = input("\nPlease type the number corresponding with the " 
    "prioritization rule you would like to use: "
    "\n    0 - No prioritization, ignore all resource constraints"
    "\n    1 - Lowest task number prioritization"
    "\n    2 - Highest resource demand"
    "\n    3 - Most total successors"
    "\n    4 - Latest finish time"
    "\n    5 - Greatest Rank Positional Weight"
    "\n    6 - Greatest Rank Positional Weight*"
    "\n    7 - Multi-Pass Prioritization\n")

    try:
        int(selected_rule) + 1 - 1
    except:
        print("\nYou have entered an invalid rule number.  Please try again.\n")
        return(selected_rule)
        select_rule()

    if int(selected_rule) >= 0 and int(selected_rule) <= 7:
        selected_rule = int(selected_rule)
        return(selected_rule)
    else:
        print("\nYou have entered an invalid rule number.  Please try again.\n")
        return(selected_rule)
        select_rule()

def schedule_in_time(project_number,job_data,task_pairs, resource_data, selected_rule):
    scheduled_tasks = []
    to_schedule = []
    task_durations = []
    schedule = {}
    
    # Create a list of tasks and lengths
    for i in range(0,len(job_data)):
        task = job_data[i]["job_number"]
        duration = job_data[i]["duration"]
        task_durations.append((task,duration))

    # Initialize timer and list of tasks still to be scheduled.
    t = 0
    limited_task_pairs = list(task_pairs)

    # Loop until all tasks have been scheduled.
    while limited_task_pairs:
        to_schedule = []
        length_exception = False

        # Try to schedule tasks whose predecessors have been scheduled.
        for k, v in limited_task_pairs:
            if k not in [i[1] for i in limited_task_pairs]:
                to_schedule.append(k)

        to_schedule = set(to_schedule)

        for i in to_schedule:
            predecessors = []
            for k, v in task_pairs:
                if v == i:
                    predecessors.append(schedule[k]["end_time"])
            # Check to see if predecessors are complete.
            # Then, check to see if this task is prioritized.
            if all(j <= t for j in predecessors):
                next_task = check_constraints(i, project_number, job_data, t, schedule, to_schedule, resource_data, selected_rule, task_pairs)
                # Check to see if this task is prioritized and then schedule if so.
                if next_task == i:
                    schedule[i] = {}
                    schedule[i]["start_time"] = t
                    for task, duration in task_durations:
                        if task == i:
                            task_length = duration
                            if task_length == 0:
                                length_exception = True
                    schedule[i]["end_time"] = schedule[i]["start_time"] + task_length

                    #If scheduled, remove task from limited task pairs.
                    limited_task_pairs = list(filter(lambda k : k[0] != i, limited_task_pairs))

        # Increment time if no tasks have zero length and repeat.
        if length_exception == False:
            t = t + 1

    # Publish the completed schedule.
    schedule_fill(project_number, job_data, schedule, selected_rule)
    #graph_schedule(project_number,job_data,schedule)

