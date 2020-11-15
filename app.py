from bs4 import BeautifulSoup
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import requests
import csv
import progressbar
import pickle
import time
import os
from ctypes import *
windll.shcore.SetProcessDpiAwareness(1)


def save_html_code(hero_name):
    '''
    WORKING
    '''
    link = 'https://www.dotabuff.com/heroes/' + \
        normalize_hero_name(hero_name) + '/counters'
    source = requests.get(link, headers={'User-agent': 'your bot 0.1'}).text
    soup = BeautifulSoup(source, 'lxml')
    html = soup.prettify("utf-8")

    with open("D:\Coding\Python\Dota 2\Heroes\Counters\\" + hero_name + ".html", "wb") as file:
        file.write(html)


def hero_data(hero):
    '''
    WORKING
    '''
    link = 'https://www.dotabuff.com/heroes/' + hero + '/counters'
    source = requests.get(link, headers={'User-agent': 'your bot 0.1'}).text
    soup = BeautifulSoup(source, 'lxml')
    html = soup.prettify("utf-8")

    i = 0
    disadvantage_array = []
    table = soup.find('table', class_="sortable")
    for entry in table.find_all('td'):
        if(i % 5 == 1):
            hero_name = entry.text
        elif(i % 5 == 2):
            hero_disadvantage = float(entry.text[:-1])
        elif (i % 5 == 4):
            hero_name = normalize_hero_name(hero_name)
            disadvantage_array.append([hero_name, hero_disadvantage])
        i = i+1
    return disadvantage_array


def find_hero_list():
    '''
    Sorted Hero list with Hero Names in lowercase and space eliminated by hyphen coz it will be appended in website link.
    WORKING
    '''
    heroes = []
    for hero in hero_data('axe'):
        hero[0] = normalize_hero_name(hero[0])
        heroes.append(hero[0])
    heroes.append('axe')
    heroes.sort()

    csvfile = open('hero_list.csv', 'w', newline='')
    obj = csv.writer(csvfile)
    i = 1
    for row in heroes:
        obj.writerow((row, i))
        i = i+1
    csvfile.close()

    return heroes


def create_disadvantage_matrix():
    '''
    Creates table if 120x120 elements and [0][0]th entry being NaN
    Rest 119 rows and column being alphabetically sorted Hero Names in lowercase and space eliminated by hyphen coz it
    will be appended in website link. WORKING
    Change find_hero_list() part
    '''
    disadvantage_matrix = [[0] * 120 for i in range(120)]
    disadvantage_matrix[0][0] = 'NaN'
    heroes = find_hero_list()
    for i in range(119):
        disadvantage_matrix[i+1][0] = heroes[i]
        disadvantage_matrix[0][i+1] = heroes[i]
    return disadvantage_matrix


def fill_disadvantage_matrix():
    '''
    Change find_hero_list() part
    '''
    heroes = find_hero_list()
    disadvantage_matrix = create_disadvantage_matrix()
    i = 1
#     widgets = [' [',progressbar.Timer(format= 'elapsed time: %(elapsed)s'), '] ',progressbar.Bar('*'),' ',progressbar.Percentage(), ' (',progressbar.ETA(), ') ',]
#     bar = progressbar.ProgressBar(max_value=120,widgets=widgets).start()
    for hero in heroes:
        specific_hero_data = hero_data(hero)
        k = 0
        for bro in specific_hero_data:
            try:
                disadvantage_matrix[disadvantage_matrix[0].index(
                    bro[0])][i] = bro[1]
            except:
                print(hero + ',' + bro[0])
#         bar.update(i)
        progress_var.set(i)
        top.update_idletasks()
        i = i+1
    progress_var.set(0)
    top.update_idletasks()
    csvfile = open('matrix.csv', 'w', newline='')
    obj = csv.writer(csvfile)
    for row in disadvantage_matrix:
        obj.writerow(row)
    csvfile.close()

    return disadvantage_matrix


def normalize_hero_name(hero_name):
    if(hero_name == 'Nature\'s Prophet'):
        hero_name = 'natures-prophet'
    else:
        hero_name = hero_name.replace(' ', '-')
        hero_name = hero_name.lower()
    return hero_name


def retrieve_hero_list():
    csvfile = open('hero_list.csv', 'r', newline='')
    obj = csv.reader(csvfile)
    hero_list = []
    while True:
        try:
            hero_list.append(next(obj))
        except:
            break
    matr = {}
    for i in range(119):
        matr[hero_list[i][0]] = hero_list[i][1]
    return matr


def retrieve_matrix():
    csvfile = open('matrix.csv', 'r', newline='')
    obj = csv.reader(csvfile)
    mat = []
    while True:
        try:
            mat.append(next(obj))
        except:
            break
    return mat


def counter_offline(names):
    heroes = retrieve_hero_list()
    matrix = retrieve_matrix()
    arr = []
    ans = []
    counters = []
    for name in names:
        try:
            temp = []
            for i in range(1, 120):
                temp.append(matrix[i][int(heroes[name])])
            arr.append(temp)
        except:
            print("Hero not found: "+name+'\n')

    for i in range(0, 119):
        s = 0
        for j in range(len(names)):
            try:
                s = s + float(arr[j][i])
            except:
                continue
        s = round(s, 2)
        ans.append(s)
    i = 0
    for a in heroes.keys():
        counters.append((ans[i], a))
        i = i+1
    counters.sort(reverse=True)
    if(arr == []):
        return 0
    return counters


def counter_update():
    fill_disadvantage_matrix()
    find_hero_list()
    update_log()
    L1.config(text=get_update_history())


def update_log():
    log = []
    if os.path.exists('update-log.dat'):
        with open('update-log.dat', 'rb') as ul:
            log = pickle.load(ul)

    update_time = time.asctime(time.localtime(time.time()))
    log.append(update_time)
    with open('update-log.dat', 'wb') as wl:
        pickle.dump(log, wl)


def get_update_history():
    log = []
    message = "Last Update : "
    if os.path.exists('update-log.dat'):
        with open('update-log.dat', 'rb') as ul:
            log = pickle.load(ul)
        return message + log[-1]
    return message + "No Update History"

###########      UI      ###########


def add_hero():
    '''
    Appends hero to internal variable
    Adds to text frame
    Clears the entry field
    '''
    name = normalize_hero_name(E1.get())
    input_heroes.append(name)
    text.configure(state='normal')
    text.insert(END, name+'\n')
    text.configure(state='disabled')
    text.pack()
    E1.delete(0, 'end')


def quit_button():
    '''
    Quits application
    '''
    top.destroy()


def clear_button():
    '''
    Clears the list
    And text field
    '''
    text.configure(state='normal')
    text2.configure(state='normal')
    text3.configure(state='normal')

    input_heroes.clear()
    text.delete(1.0, END)
    text2.delete(1.0, END)
    text3.delete(1.0, END)

    text.configure(state='disabled')
    text2.configure(state='disabled')
    text3.configure(state='disabled')

    E1.delete(0, 'end')


def find_counter():
    '''
    Calls the function finding the required counters list for the input heroes
    '''
    # Call hero name to hero number
    # Saved csv file, retrieve data
    # Save in "counters" variable
    error_message = "N.A.\nThis error occurs if all the input heroes doesn't exist in DoTA2"
    counters = counter_offline(input_heroes)
    if(counters == 0):
        text2.configure(state='normal')
        text2.delete(1.0, END)
        text2.insert(END, error_message)
        text2.configure(state='disabled')
    else:
        text2.configure(state='normal')
        text2.delete(1.0, END)
        for i in range(1, 18):
            text2.insert(END, str(i)+": " +
                         counters[i-1][1] + ' - ' + str(counters[i-1][0]) + '\n')
        text2.configure(state='disabled')

        text3.configure(state='normal')
        text3.delete(1.0, END)
        for i in range(18, 36):
            text3.insert(END, str(i)+": " +
                         counters[i-1][1] + ' - ' + str(counters[i-1][0]) + '\n')
        text3.configure(state='disabled')


def clear_heroes():
    text.configure(state='normal')
    input_heroes.clear()
    text.delete(1.0, END)
    text.configure(state='disabled')


input_heroes = []

### Colors ###
# Background #2c152b
# Foreground #801437
# Button #4f0f32
# TextArea #801437
# ButtonText #fef389
# TextAreaText #ffffff


# Main window
top = Tk()
top.geometry("600x700")
top.title("Counters App")
top.configure(bg='#2c152b')
top.iconbitmap(r'Dota-2.ico')

# Label for entry bar
L1 = Label(top, text="Enter Hero Name:", bg="#2c152b",
           fg="#fef389")
L1.place(x=5, y=0)

# The entry bar
E1 = Entry(top, bd=1, bg="#801437", fg="#ffffff", insertbackground="#ffffff")
E1.place(y=27, width=600)

# Add hero button
BA = Button(top, text="Add Hero", command=add_hero, bg="#4f0f32", fg="#fef389")
BA.place(relx=0.5, y=50, anchor="n")

# Selected hero list frame
text_frame = Frame(top, bg="#801437", height=100, width=600)
text_frame.place(relx=0.5, y=85, anchor='n', height=100, width=600)

# The text bar
text = Text(text_frame, bg='#801437', fg="#ffffff", padx=10)
text.place(height=100, width=600)
text.configure(state='disabled')

# Find Counters' Button
BC = Button(top, text="Find Counters", command=find_counter,
            bg="#4f0f32", fg="#fef389")
BC.place(relx=0.3, y=185, anchor='n')

# Clear Counters' List Button
BL = Button(top, text="Clear Heroes", command=clear_heroes,
            bg="#4f0f32", fg="#fef389")
BL.place(relx=0.7, y=185, anchor='n')

# Label for counters
L1 = Label(top, text="The counters are:",
           bg="#2c152b", fg="#fef389")
L1.place(x=5, y=230, anchor='nw')

# Counters List
text2 = Text(top, bg='#801437', fg="#ffffff", padx=5, font="courier 10")
text2.place(x=0, y=255, height=345, width=300)
text2.configure(state='disabled')

# Counters List #2
text3 = Text(top, bg='#801437', fg="#ffffff", padx=5)
text3.place(x=300, y=255, height=345, width=300)
text3.configure(state='disabled')

# Latest Update History
L1 = Label(top, text=get_update_history(), bg="#2c152b", fg="#fef389")
L1.place(relx=0.5, y=615, anchor='center')

# Progress bar
progress_var = DoubleVar()
s = ttk.Style()
s.configure("bar.Horizontal.TProgressbar", troughcolor="#ffffff", bordercolor="#ffffff",
            background="#000000", lightcolor="#000000", darkcolor="#000000")
progressbar = ttk.Progressbar(
    top, variable=progress_var, maximum=120, mode="determinate")
progressbar.place(relx=0.5, y=640, anchor="center", width=200)

# Update Button
BU = Button(top, text="Update", command=counter_update,
            bg="#4f0f32", fg="#fef389")
BU.place(relx=0, rely=1, anchor="sw")

# Clear All Button
BC = Button(top, text="Clear All", command=clear_button,
            bg="#4f0f32", fg="#fef389")
BC.place(relx=0.5, rely=1, anchor="s")

# Quit Button
BQ = Button(top, text="Quit", command=quit_button, bg="#4f0f32", fg="#fef389")
BQ.place(relx=1, rely=1, anchor="se")


top.mainloop()
