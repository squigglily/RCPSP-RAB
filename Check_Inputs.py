def main():
    import sys
    import re
    import csv

    problem_files = []

    for i in range(1,49):
        for j in range(1, 11):
            file = "/home/squigglily/Documents/School Stuff/Grad School/Independent_Study/RCP/J30" + str(i) + "_" + str(j) + ".RCP"
            project = "J30" + str(i) + "_" + str(j)
            check_if_bad(file, project, problem_files)

    print(problem_files)

def check_if_bad(file, project, problem_files):
    import sys
    import re
    import csv

    problem_file = False

    f = open(file,"r")
    raw_data = f.read()
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
        resource_count = 0

        for j in range(0,len(resources)):
            if int(resources[j]) > 0:
                resource_count = resource_count + 1

        if resource_count > 1:
            problem_file = True

    if problem_file == False:
        problem_files.append(project)

    return(problem_files)

def find_nth(haystack, needle, n):
    start = haystack.find(needle)

    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1

    return start