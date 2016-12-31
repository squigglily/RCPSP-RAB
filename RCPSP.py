def main():
    openfile()

def openfile():
    file = input("Please type the filename (including path) for the project:")
    f = open(file,"r")
    raw_data = f.read()
    if raw_data[0].isnumeric():
        print("Number")
    elif raw_data[0] == "R":
        print("Text")
    else:
        print("Error")

