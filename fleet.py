#################################################
#|                FLEET MANAGER                |#
#|        Fall 2021 CISP 71 CRUD Project       |#
#################################################

# tkinter and improved themed ttk
import tkinter as tk
import tkinter.ttk as ttk

# Various message boxes for warnings, prompts, and errors
from tkinter import simpledialog
from tkinter.messagebox import askokcancel, askyesno, showerror, showinfo, WARNING, showwarning

# sqlite3 and error handling
import sqlite3 as sql
from sqlite3 import Error
from sqlite3.dbapi2 import DatabaseError

#################################################
#| Global Dictionary of SQL Columns/Fields     |#
#################################################

# Ordered and centralized list of database columns
# Dictionaries for each column allow customization of behavior
# The first dictionary is the primary key v_num
# The main and child window classes will loop through this list and use the dictionary keys to dynamically place widgets in an ordered manner, get user values, and fetch database values

fields = (
    {
        'column': 'v_num',
        'type': 'number',
        'label': 'Vehicle #',
        'dash_width': 75,
        'search_by': 'string',
        'entry_width': 50
        },
    {
        'column': 'vin',
        'type': 'text',
        'label': 'VIN',
        'dash_width': 150,
        'search_by': 'string',
        'entry_width': 50
        },
    {
        'column': 'dept',
        'type': 'text',
        'label': 'Department',
        'dash_width': 100,
        'search_by': 'dropdown',
        'dropdown_values': ('', 'Executive', 'Parks', 'Utilities', 'Finance', 'Building & Safety', 'Environmental', 'UAP Task Force'),
        'dropdown_width': 20
        },
    {
        'column': 'year',
        'type': 'number',
        'label': 'Year',
        'dash_width': 35,
        'search_by': 'string',
        'entry_width': 50
        },
    {
        'column': 'make',
        'type': 'text',
        'label': 'Make',
        'dash_width': 100,
        'search_by': 'string',
        'entry_width': 50
        },
    {
        'column' : 'model',
        'type': 'text',
        'label': 'Model',
        'dash_width': 100,
        'search_by': 'string',
        'entry_width': 50
        },
    {
        'column': 'class',
        'type': 'text',
        'label': 'Vehicle Class',
        'dash_width': 100,
        'search_by': 'dropdown',
        'dropdown_values': ('', 'Compact', 'Full-size', 'Van', 'Light truck', 'Heavy duty truck', 'Bird'),
        'dropdown_width': 20
        },
    {
        'column': 'lic',
        'type': 'text',
        'label': 'License Plate',
        'dash_width': 100,
        'search_by': 'string',
        'entry_width': 50
        },
    {
        'column': 'motor',
        'type': 'text',
        'label': 'Motor Type',
        'dash_width': 80,
        'search_by': 'radio',
        'radio_values': ('Gas', 'Diesel', 'CNG', 'Hybrid', 'Electric')
        },
    {
        'column' : 'retired',
        'type' : 'string',
        'label': 'Retired?',
        'dash_width': 60,
        'search_by': 'radio',
        'radio_values': ('Yes', 'No')
        },
    {
        'column' : 'notes',
        'type' : 'text',
        'label': 'Notes',
        'dash_width': 200,
        'search_by': 'string',
        'entry_width': 50,
        'box_width': 10,
        'box_height': 15
        }
    )

#################################################
#| SQLite Database Interface Class             |#
#################################################

class DataInterface:

    global fields
    
    def __init__(self, db_path, parent):
        self.parent = parent

        #For each field, get the column name and sql type and append them to a list as a combined string
        keys = []
        for i in range(1, len(fields)):
            column_name = fields[i]['column']
            column_type = fields[i]['type']
            keys.append(str(column_name) + ' ' + str(column_type))

        #Concatenate/join the strings to create a valid SQL command
        cmd = 'CREATE TABLE IF NOT EXISTS fleet (v_num integer PRIMARY KEY, ' + ', '.join(keys[0:-1]) + ', ' + keys[-1] + ');'

        #Initialize the connection
        self.conn = None
        try:
            self.conn = sql.connect(db_path)
            self.curr = self.conn.cursor()
            self.ExecuteStatement(cmd, '')
            self.parent.Log('Connected to ' + db_path)
        except Error as e:
            self.parent.Log(e)

    # SQL statement execution method
    #   statement: the SQL command string
    #   placeholders: list of strings for parameterized statements
    def ExecuteStatement(self, statement, placeholders):
        self.curr.execute(statement, placeholders)
        self.conn.commit()
    
    # Select a record by unique ID
    def SelectRecord(self, id):
        cmd = 'SELECT * FROM fleet WHERE v_num = ?;'
        self.ExecuteStatement(cmd,(id,))
        return self.curr.fetchone()
    
    # Add a new record, values to create the record are passed into the function as a list
    def AddRecord(self, values):
        columns = []
        for i in range(0, len(fields)):
            columns.append(fields[i]['column'])

        #Assemble SQL command by concatenating/joining strings in the column and value lists
        cmd = 'INSERT INTO fleet (' + ', '.join(columns) + ') VALUES (' + (len(fields)-1)*'?,' + '?);'
        
        try:
            self.ExecuteStatement(cmd, values)
            self.parent.Log("Vehicle #" + str(values[0]) + " added to database.")
        except Error as e:
            self.parent.Log("Error in adding record: " + str(e))
            self.conn.rollback()
            return e
    
    # Delete a record, checks first if the record exists by verifying that SelectRecord() returns a record
    def DeleteRecord(self, id):
        if self.SelectRecord(id) is not None:
            cmd = 'DELETE FROM fleet WHERE v_num = ?;'
            try:
                self.ExecuteStatement(cmd, (id,))
                self.parent.Log('Deleted Vehicle #' + str(id) + '.')
            except Error as e:
                self.parent.Log("Error deleting records: " + str(e))
                self.conn.rollback()
                return e

    # Update an existing record
    def UpdateRecord(self, values):
        columns = []
        for i in range(0, len(fields)):
            columns.append(fields[i]['column'])

        cmd = 'UPDATE fleet SET ' + ' = ?, '.join(columns[1:]) + ' = ? WHERE ' + columns[0] + ' = ?;'
        
        try:
            self.ExecuteStatement(cmd, values)
            self.parent.Log("Vehicle #" + str(values[-1]) + " updated.")
        except Error as e:
            self.parent.Log("Error updating Vehicle #" + str(values[-1]) + " record: " + str(e))
            self.conn.rollback()
            return e

    # Select all records, return fetchall() list of records/values
    def SelectAllRecords(self):
        cmd = 'SELECT * FROM fleet'
        self.ExecuteStatement(cmd,'')
        return self.curr.fetchall()
    
    # Filter Records based on user query
    #   Parameter fields is a list containing tuple pairs, each pair contains the column name and a boolean for a wildcard search
    #   Parameter values is the list of corresponding query values

    def FilterRecords(self, fields, values):
        #Assemble the WHERE clauses of the SQL command based on column name and whether a wildcard (%) was used
        #The bool isWildSearch is determined by logic in the InspectRecordWindow class
        where = []
        for column, isWildSearch in fields:
            if(isWildSearch):
                where.append(column + " LIKE ?")
            else:
                where.append(column + ' = ?')

        #Example command string: 'SELECT * FROM fleet WHERE v_num = 555555 AND make LIKE ?;'
        cmd = 'SELECT * FROM fleet WHERE ' + ' AND '.join(where) + ';'

        #Execute statement, check the number of records and print to console, return the result, rollback any errors
        try:
            self.ExecuteStatement(cmd, values)
            result = self.curr.fetchall()
            num_records = len(result)
            if num_records == 0:
                self.parent.Log('The query returned 0 records.')
                return None
            elif num_records != 1:
                self.parent.Log('The query returned {} records.'.format(num_records))
                return result
            else:
                self.parent.Log('The query returned 1 record.')
                return result
        except Error as e:
            self.parent.Log('Search error: ' + str(e))
            self.conn.rollback()
            return e
    
    # Select a column value from a unique ID
    def GetRecordValue(self, field, id):
        cmd = 'SELECT ' + field + ' FROM fleet WHERE v_num = ?;'
        self.ExecuteStatement(cmd,(id,))
        return self.curr.fetchone()[0]

#################################################
#| Main App Window Class                       |#
#################################################

# MainAppWindow inherits from the root window class tk.Tk
# MainAppWindow is called when this file is run as the main program
# Children window classes FilterWindow, InspectRecordWindow, and AddRecordWindow are instantiated when the user clicks the corresponding buttons

class MainAppWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)
        self.title('Fleet Manager')
        self.iconphoto(True, tk.PhotoImage(file='HWcar-5-icon.png'))

    # CenterWindow calculates offset values based on the window size to position the window in the center of the screen
    def CenterWindow(self):
        #update_idletasks() is required for winfo_width and winfo_height to return the correct values
        self.update_idletasks()

        #Get the current width and height of the window
        windowWidth = self.winfo_width()
        windowHeight = self.winfo_height()

        #Determine the offset values
        xOffset = int(self.winfo_screenwidth()/2 - windowWidth/2)
        yOffset = int(self.winfo_screenheight()/2 - windowHeight/2)
        
        self.geometry('+{}+{}'.format(xOffset, yOffset))

    # Create the reference to the database interface
    def LinkDatabase(self):
        dbFilename = 'fleet.db'
        self.database = DataInterface(dbFilename, self)
    
    # Create the frames, treeview table, buttons, labels, etc.
    def CreateDashboard(self):
        global fields
        
        #Bool for tracking if any treeview items are selected
        self.isListSelected = False

        self.dashFrame = ttk.LabelFrame(self, text='Dashboard')
        self.dashFrame.pack(padx=5, pady=5, fill='x')
        
        #Filter function buttons
        self.filterFrame = ttk.Frame(self.dashFrame)
        self.filterFrame.grid(row=0, sticky='ew')
        self.newFilterButton = ttk.Button(self.filterFrame, text='New Filter', command=self.OpenFilterWindow)
        self.newFilterButton.pack(padx=5, pady=5, side='left')
        self.modifyFilterButton = ttk.Button(self.filterFrame, text='Modify Filter', state=tk.DISABLED, command=lambda : self.FilterWindowHandler(filterStatus = 'modifying'))
        self.modifyFilterButton.pack(padx=5, pady=5, side='left')
        self.clearFilterButton = ttk.Button(self.filterFrame, text='Clear Filter', state=tk.DISABLED, command=lambda : self.FilterWindowHandler(filterStatus = 'clearing'))
        self.clearFilterButton.pack(padx=5, pady=5, side='left')
        
        #Vehicle List treeview table
        self.tableFrame = ttk.Frame(self.dashFrame)
        self.tableFrame.grid(row=1)
        self.vehicleTable = ttk.Treeview(self.tableFrame, height=10)
        self.vehicleTable.grid(row=0, column=0, padx=5, pady=5)
        self.vehicleTable['columns'] = list(range(len(fields)))
        self.vehicleTable['show'] = 'headings'
        
        #Bind methods to handle treeview item selection and double clicking
        self.vehicleTable.bind('<<TreeviewSelect>>', self.GetSelectedIDs)
        self.vehicleTable.bind('<Double-1>', self.DoubleClickInspect)

        #Set the treeview headings and column widths by looping through their values in the fields dictionary
        for i in range((len(fields))):
            heading_text = fields[i]['label']
            dash_width = fields[i]['dash_width']
            self.vehicleTable.column(i, anchor=tk.W, width=dash_width, minwidth=dash_width, stretch=0)
            self.vehicleTable.heading(i, text=heading_text, anchor=tk.W)

        #X and Y Scrollbars to scroll through the content
        self.tableYScroll = ttk.Scrollbar(self.tableFrame, orient=tk.VERTICAL, command=self.vehicleTable.yview)
        self.vehicleTable.configure(yscroll=self.tableYScroll.set)
        self.tableYScroll.grid(row=0, column=1, sticky='ns')
        self.tableXScroll = ttk.Scrollbar(self.tableFrame, orient=tk.HORIZONTAL, command=self.vehicleTable.xview)
        self.vehicleTable.configure(xscroll=self.tableXScroll.set)
        self.tableXScroll.grid(row=1, column=0, sticky='ew')

        #listButtonFrame contains buttons for inspecting, deleting, and adding records
        self.listButtonFrame = ttk.Frame(self.dashFrame)
        self.listButtonFrame.grid(row=2, sticky='nsew')
        self.inspectVehicleButton = ttk.Button(self.listButtonFrame, text='Inspect Selected Vehicles', state=tk.DISABLED, command=self.InspectSelectedRecords)
        self.inspectVehicleButton.pack(padx=5, pady=5, side='left')
        self.deleteVehicleButton = ttk.Button(self.listButtonFrame, text='Delete Selected Vehicles', state=tk.DISABLED, command=self.DeleteSelectedRecords)
        self.deleteVehicleButton.pack(padx=5, pady=5, side='left')
        ttk.Button(self.listButtonFrame, text='Add New Vehicle', command=lambda : NewRecordWindow(self)).pack(padx=5, pady=5, side='right')
        ttk.Button(self.listButtonFrame, text='Inspect by Vehicle #', command=self.InspectByIdDialog).pack(padx=5, pady=5, side='right')

        #Text widget for displaying a log of activities
        self.logLine = 0
        self.logFrame = ttk.LabelFrame(self.dashFrame, text='Operation Log')
        self.logFrame.grid(row=3, padx=5, pady=5)
        self.logTextBox = tk.Text(self.logFrame, height=5, width=137, state=tk.DISABLED)
        self.logTextBox.pack(padx=5, pady=5, side='left')
        self.logYScroll = ttk.Scrollbar(self.logFrame, orient=tk.VERTICAL, command=self.logTextBox.yview)
        self.logTextBox.configure(yscroll=self.logYScroll.set)
        self.logYScroll.pack(side='left', fill='y', padx=5)
        
        #Status bar at the bottom of the window indicates some current info
        self.statusBar = ttk.Frame(self)
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tablePopulation = tk.StringVar(self)
        ttk.Label(self.statusBar, textvariable=self.tablePopulation).pack(side='left', padx=5)
        self.filterIndicator = tk.StringVar(self, 'Current Filters: None')
        ttk.Label(self.statusBar, textvariable=self.filterIndicator).pack(side='right', padx=5)
    
    # Method for populating the table initially, or refreshing the vehicle table after adding, deleting, and modifying records
    def PopulateVehicleTable(self, dbEntries):
        self.vehicleTable.selection_remove(self.vehicleTable.selection())
        for item in self.vehicleTable.get_children():
            self.vehicleTable.delete(item)
        for entry in dbEntries:
            self.vehicleTable.insert('', tk.END, values=entry)
        
        #Status bar updates whenever we re-populate the table
        display_pop = len(dbEntries)
        total_pop = len(self.database.SelectAllRecords())
        self.tablePopulation.set('Displaying {} out of {} database records.'.format(display_pop, total_pop))

    # Method for printing strings to self.logTextBox
    def Log(self, entry):
        self.logTextBox['state'] = tk.NORMAL
        self.logTextBox.insert(tk.END, str(self.logLine) + ': ' + entry + '\n')
        self.logTextBox.see(tk.END)
        self.logTextBox['state'] = tk.DISABLED
        self.logLine += 1
    
    # Instantiate a new filter window and pass a reference to self
    def OpenFilterWindow(self):
        self.filterWindow = FilterWindow(self)
    
    # Method to handle the status of the filter, hiding and showing the filter window appropriately
    def FilterWindowHandler(self, filterStatus):
        #After executing a filter
        if filterStatus == 'executed':
            self.filterWindow.withdraw()
            self.filterWindow.grab_release()
            self.filterWindow.focus_lastfor()
            self.modifyFilterButton['state'] = tk.NORMAL
            self.clearFilterButton['state'] = tk.NORMAL
            self.newFilterButton['state'] = tk.DISABLED
            self.filterIndicator.set('Current Filters: {}'.format(self.filterWindow.GetQueryIndicator()))
        #After clicking the modify filter button
        elif filterStatus == 'modifying':
            self.filterWindow.filterStatus = filterStatus
            self.filterWindow.deiconify()
            self.filterWindow.focus_set()
            self.filterWindow.grab_set()
        #After clicking the clear filter button
        elif filterStatus == 'clearing':
            self.Log('Clearing filters...')
            self.filterWindow.destroy()
            self.PopulateVehicleTable(self.database.SelectAllRecords())
            self.modifyFilterButton['state'] = tk.DISABLED
            self.clearFilterButton['state'] = tk.DISABLED
            self.newFilterButton['state'] = tk.NORMAL
            self.filterIndicator.set('Current Filters: None')

    # Method for handling the selection of rows in the treeview
    def GetSelectedIDs(self, event):
        selection = self.vehicleTable.selection()
        self.selected_ids = []
        
        for row in selection:
            self.selected_ids.append(self.vehicleTable.item(row)['values'][0])

        if(len(self.selected_ids) > 0):
            self.isListSelected = True
        else:
            self.isListSelected = False
        
        self.ToggleListButtons()

    # Method for setting the state of the list buttons based on isListSelected
    def ToggleListButtons(self):
        if self.isListSelected:
            self.inspectVehicleButton['state'] = tk.NORMAL
            self.deleteVehicleButton['state'] = tk.NORMAL
        else:
            self.inspectVehicleButton['state'] = tk.DISABLED
            self.deleteVehicleButton['state'] = tk.DISABLED
    
    # Method called by the Delete Selected Record button
    # Can handle whether a single or multiple records were selected for deletion
    def DeleteSelectedRecords(self):
        answer = askyesno(title='Delete records?', message='Are you sure you want to delete the selected records? You cannot undo this action.', icon=WARNING, parent=self)
        if answer:
            try:
                for id in self.selected_ids:
                    result = self.database.DeleteRecord(id)
                    if result == None:
                        showinfo(title='Record deleted', message='Vehicle # {} was successfully deleted.'.format(id), parent=self)
                        self.PopulateVehicleTable(self.database.SelectAllRecords())
                    else:
                        raise DatabaseError
            except DatabaseError:
                showwarning(title='Error', message='A record could not be deleted. No further actions will be taken.', parent=self)
        else:
            return

    # Event handler method for double clicking a row in the treeview vehicle list
    def DoubleClickInspect(self, event):
        for id in self.selected_ids:
            InspectRecordWindow(self, id)
    
    # Method for the inspectVehicleButton
    def InspectSelectedRecords(self):
        for id in self.selected_ids:
            InspectRecordWindow(self, id)
    
    # Method for the Inspect by Vehicle # button
    def InspectByIdDialog(self):
        answer = simpledialog.askinteger('Input by Vehicle #', 'What is the Vehicle #?', parent=self)
        
        if answer is not None:
            if self.database.SelectRecord(answer) is not None:
                InspectRecordWindow(self,str(answer))
            else:
                showwarning(title='Warning', message='Record does not exist', parent=self)
        else:
            return
    
    # Method Run() is called in the __main__ program to start the program
    def Run(self):
        self.CreateDashboard()
        self.LinkDatabase()
        self.CenterWindow()
        self.PopulateVehicleTable(self.database.SelectAllRecords())
        self.mainloop()

#################################################
#| Table Filter Top Window Class               |#
#################################################

# The code is structured for one FilterWindow class to be instantiated at a time
# The instantiated FilterWindow class is assigned to the variable self.filterWindow
# Functions can then be called on that instance from MainAppWindow
class FilterWindow(tk.Toplevel):
    global fields

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        #Set window properties
        self.title('List Filter')
        self.resizable(False, False)
        self.focus_set()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.ConfirmCancel)

        #Initialize an instance variable to track the status of the filter
        self.filterStatus = 'new'

        self.CreateFilterForm()

    def CreateFilterForm(self):
        formHeaderFrame = ttk.Frame(self)
        formHeaderFrame.pack(padx=5, pady=5, fill='x')
        header_text = 'Enter values to filter the vehicle list. Use "%" as a wildcard placeholder.'
        ttk.Label(formHeaderFrame, text=header_text).pack(padx=5, pady=5, fill='x')

        formFrame = ttk.LabelFrame(self, text='Fields')
        formFrame.pack(padx=5, pady=(5,10), fill='x')

        #Loop through fields and generate labels with text from the ['label'] key for each field dictionary
        for i in range(len(fields)):
            ttk.Label(formFrame, text=fields[i]['label']).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
        
        #List for storing the string variables in the widgets
        self.string_vars = []
        #List variable for storing references to the widget objects
        self.form_widgets = []

        #Create the string variables and widgets and append them to the lists
        for i in range(len(fields)):
            self.string_vars.append(tk.StringVar(self, ''))

            #Widget types are determined by the 'search_by' key
            if(fields[i]['search_by'] == 'dropdown'):
                dropdown = fields[i]['dropdown_values']
                self.form_widgets.append(ttk.Combobox(formFrame, width=fields[i]['dropdown_width'], textvariable=self.string_vars[i], values=dropdown, state='readonly'))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            elif(fields[i]['search_by'] == 'radio'):
                self.form_widgets.append(ttk.Frame(formFrame))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
                for radio_value in fields[i]['radio_values']:
                    ttk.Radiobutton(self.form_widgets[i], text=radio_value, value=radio_value, variable=self.string_vars[i]).pack(padx=5, pady=5, side='left')
            else:
                self.form_widgets.append(ttk.Entry(formFrame, width=fields[i]['entry_width'], textvariable=self.string_vars[i]))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)

        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(padx=5, pady=5, fill='x')
        ttk.Button(buttonFrame, text='Clear Fields', command=self.ClearFields).pack(side='left')
        ttk.Button(buttonFrame, text='Submit', command=self.BuildValues).pack(side='right')
        ttk.Button(buttonFrame, text='Cancel', command=self.ConfirmCancel).pack(side='right')
    
    # Clears each field of any input by the user
    def ClearFields(self):
        for i in range(len(self.string_vars)):
            self.string_vars[i].set('')
    
    # Assembles each StringVar into a format that works with the database method FilterRecords()
    def BuildValues(self):
        #field_pairs contains a list of tuple pairs indicating the column type and if the search uses a wildcard or not
        field_pairs = []
        #value_list are the actual values to search by
        value_list = []
        #variable stores the list of columns in the query (to update the status bar)
        self.query_columns = []

        self.parent.Log('Building filter query...')
        
        #Loop through all StringVar values and append only non-empty values
        for i in range(len(self.string_vars)):
            value = self.string_vars[i].get()
            if value == '':
                continue
            else:
                if fields[i]['search_by'] == 'string':
                    if '%' in value:
                        #If '%' is in the string, the tuple pair is the column name and True
                        field_pairs.append((fields[i]['column'], True))
                    else:
                        #If not, then the tuple pair is the column name and False
                        field_pairs.append((fields[i]['column'], False))
                else:
                    #For any other column (i.e. dropdowns and radio buttons), we don't need a wildcard search, so the tuple pair is always column name and False
                    field_pairs.append((fields[i]['column'], False))
                
                value_list.append(value)
                self.query_columns.append((fields[i]['label']))

        if len(value_list) == 0:
            showwarning(title='Warning', message='You must enter at least one query field.', parent=self)
            return
        else:
            self.RunQuery(field_pairs, value_list)
    
    # Send the built lists to main window app, main window app populates vehicle table
    def RunQuery(self, field_pairs, value_list):
        try:
            result = self.parent.database.FilterRecords(field_pairs, value_list)
            if result == None:
                none_msg = 'No records matched the filter. Try narrowing your search or use wildcards.'
                showinfo(title='No results', message=none_msg, parent=self)
                return
            else:
                self.parent.PopulateVehicleTable(result)
                self.filterStatus = 'executed'
                self.parent.FilterWindowHandler(self.filterStatus)
        except DatabaseError:
            showerror(title='Error', message='There was a problem adding the record: ' + str(result) + '.')
    
    # Method called by main app window to update the status bar
    def GetQueryIndicator(self):
        return ', '.join(self.query_columns)
    
    # Handling of the cancel/close buttons is required to ensure logical functioning of the filter window
    def ConfirmCancel(self):
        answer = askyesno(title='Cancel entry?', message='Are you sure you want to cancel the filter?', icon=WARNING, parent=self)
        if answer:
            if self.filterStatus == 'modifying':
                self.filterStatus = 'executed'
                self.parent.FilterWindowHandler(self.filterStatus)
                return
            else:
                self.destroy()
        else:
            return

#################################################
#| Inspect Record Top Window Class             |#
#################################################

# As with the FilterWindow, InspectRecordWindow inherits from Toplevel and is called by the parent main app when needed
# Multiple instances of InspectRecordWindow can be instantiated (i.e. user selected multiple rows and clicked the Inspect Selected Vehicle button)
# Creating the form, assembling values, and sending values to the database largely follows the same logic as in the filter window

class InspectRecordWindow(tk.Toplevel):
    def __init__(self, parent, id):
        super().__init__(parent)
        self.title('Record Inspector - Vehicle # ' + str(id))
        self.protocol('WM_DELETE_WINDOW', self.ConfirmCancel)
        self.resizable(False, False)
        
        self.parent = parent
        self.record_id = id

        self.parent.Log('Opened Vehicle #' + str(self.record_id) + ' for inspection.')

        self.CreateInspectionForm()
    
    def CreateInspectionForm(self):
        #Track modification of form and change style if modified
        self.modified = False
        self.style = ttk.Style()
        self.style.configure('modified.TLabel', foreground='red')

        formHeaderFrame = ttk.Frame(self)
        formHeaderFrame.pack(padx=5, pady=5, fill='x')
        header_text = 'Enter new values. Field labels change to red when modified.'
        ttk.Label(formHeaderFrame, text=header_text).pack(padx=5, pady=5, fill='x')

        formFrame = ttk.LabelFrame(self, text='Fields')
        formFrame.pack(padx=5, pady=(5,10), fill='x')

        #List variable to store the column labels and reference later to change style after form is modified
        self.field_labels = []
        for i in range(len(fields)):
            self.field_labels.append(ttk.Label(formFrame, text=fields[i]['label']))
            self.field_labels[i].grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.string_vars = []
        self.form_widgets = []

        for i in range(len(fields)):
            field_value = str(self.parent.database.GetRecordValue(fields[i]['column'], self.record_id))
            self.string_vars.append(tk.StringVar(self, field_value))

            if(fields[i]['search_by'] == 'dropdown'):
                dropdown = fields[i]['dropdown_values']
                self.form_widgets.append(ttk.Combobox(formFrame, width=fields[i]['dropdown_width'], textvariable=self.string_vars[i], values=dropdown, state='readonly'))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            elif(fields[i]['search_by'] == 'radio'):
                self.form_widgets.append(ttk.Frame(formFrame))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
                for radio_value in fields[i]['radio_values']:
                    ttk.Radiobutton(self.form_widgets[i], text=radio_value, value=radio_value, variable=self.string_vars[i]).pack(padx=5, pady=5, side='left')
            else:
                self.form_widgets.append(ttk.Entry(formFrame, width=fields[i]['entry_width'], textvariable=self.string_vars[i]))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
                if fields[i]['column'] == 'v_num' or fields[i]['column'] == 'vin':
                    self.form_widgets[i]['state'] = tk.DISABLED
            
            self.string_vars[i].trace('w', lambda a, b, c, field_index=i : [self.OnFieldChange(a, b, c, field_index), self.NumberChecker(a, b, c, field_index)])

        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(padx=5, pady=5, fill='x')
        ttk.Button(buttonFrame, text='Delete Record', command=self.DeleteRecord).pack(side='left')
        ttk.Button(buttonFrame, text='Submit Changes', command=self.BuildValues).pack(side='right')
        ttk.Button(buttonFrame, text='Cancel', command=self.ConfirmCancel).pack(side='right')
    
    #Change the column label color if a field was modified
    def OnFieldChange(self, a, b, c, field_index):
        self.modified = True
        self.field_labels[field_index]['style'] = 'modified.TLabel'
    
    #Check the number input for invalid characters and delete them
    def NumberChecker(self, a, b, c, field_index):
        current_string = self.string_vars[field_index].get()
        if fields[field_index]['type'] == 'number':
            if not current_string.isnumeric():
                if len(current_string) == 1:
                    self.string_vars[field_index].set('')
                else:
                    self.string_vars[field_index].set(current_string[0:-1])
                showwarning(title='Warning', message='This field can only contain numbers', parent=self)
    
    # Build a list with the correct order for the database function, then forward for user confirmation
    def BuildValues(self):
        self.parent.Log('Building value changes...')
        value_list = []

        for i in range(len(self.string_vars)):
            value_list.append(self.string_vars[i].get())
        
        #The database function UpdateRecord requires the unique ID to be at the end of the list
        id = value_list.pop(0)
        value_list.append(id)

        self.AskChangeCancel(value_list)
    
    # Method confirms the user's intent to change the record
    def AskChangeCancel(self, values):
        answer = askokcancel(title='Submit the changes?', message='Click OK to commit the changes to the database.', icon=WARNING, parent=self)
        if answer:
            #Check if record exists before proceeding
            if self.parent.database.SelectRecord(str(values[-1])) is not None:
                try:
                    result = self.parent.database.UpdateRecord(values)
                    if result == None:
                        showinfo(title='Record updated', message='The database was updated successfully.', parent=self)
                        self.parent.PopulateVehicleTable(self.parent.database.SelectAllRecords())
                        self.destroy()
                    else:
                        raise DatabaseError
                except DatabaseError:
                    showerror(title='Error', message='There was a problem modifying the record: ' + str(result) + '.', parent=self)
            else:
                showerror(title='Record missing', message='The inspected record no longer exists. Close the record inspector to refresh the vehicle list.', parent='self')

    def DeleteRecord(self):
        answer = askyesno(title='Delete record?', message='Are you sure you want to delete the selected records? You cannot undo this action.', icon=WARNING)
        if answer:
            try:
                result = self.parent.database.DeleteRecord(self.record_id)
                if result == None:
                    showinfo(title='Record deleted', message='Vehicle # {} was successfully deleted.'.format(self.record_id), parent=self)
                    self.parent.PopulateVehicleTable(self.parent.database.SelectAllRecords())
                    self.destroy()
                else:
                    raise DatabaseError
            except DatabaseError:
                showwarning(title='Error', message='A record could not be deleted. No further actions will be taken.', parent=self)
    
    # Confirm cancellation of form if it was modified
    def ConfirmCancel(self):
        if self.modified:
            answer = askyesno(title='Cancel entry?', message='Changes to the record will be lost if you cancel. Are you sure you want to cancel?', icon=WARNING, parent=self)
            if answer:
                self.destroy()
            else:
                return
        else:
            self.destroy()

#################################################
#| New Record Window Class                     |#
#################################################

# As with InspectRecordWindow, we don't need to instantiate a variable referencing an instance of this class
# Only one of these windows at a time can be called, since we grab and keep focus from the main window

class NewRecordWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Enter New Vehicle Information')
        self.focus_set()
        self.grab_set()
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.ConfirmCancel)

        self.parent = parent
        
        self.createAddForm()

    def createAddForm(self):
        formHeaderFrame = ttk.Frame(self)
        formHeaderFrame.pack(padx=5, pady=5, fill='x')
        header_text = 'VIN is required and cannot be changed after adding the record to the database.'
        ttk.Label(formHeaderFrame, text=header_text, wraplength=400, justify='left').pack(padx=5, pady=5, fill='x')

        formFrame = ttk.LabelFrame(self, text='Fields')
        formFrame.pack(padx=5, pady=(5,10), fill='x')

        for i in range(len(fields)):
            ttk.Label(formFrame, text=fields[i]['label']).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.string_vars = []
        self.form_widgets = []

        for i in range(len(fields)):
            self.string_vars.append(tk.StringVar(self,''))
            
            if(fields[i]['search_by'] == 'dropdown'):
                dropdown = fields[i]['dropdown_values']
                self.form_widgets.append(ttk.Combobox(formFrame, width=fields[i]['dropdown_width'], textvariable=self.string_vars[i], values=dropdown, state='readonly'))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            elif(fields[i]['search_by'] == 'radio'):
                self.form_widgets.append(ttk.Frame(formFrame))
                self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
                for radio_value in fields[i]['radio_values']:
                    ttk.Radiobutton(self.form_widgets[i], text=radio_value, value=radio_value, variable=self.string_vars[i]).pack(padx=5, pady=5, side='left')
            else:
                #Auto generate the v_num value, prevent user entry
                if(fields[i]['column'] == 'v_num'):
                    self.form_widgets.append(ttk.Entry(formFrame, width=fields[i]['entry_width'], textvariable=self.string_vars[i], state=tk.DISABLED))
                    self.string_vars[i].set(self.GetNewID())
                    self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
                else:
                    self.form_widgets.append(ttk.Entry(formFrame, width=fields[i]['entry_width'], textvariable=self.string_vars[i]))
                    self.form_widgets[i].grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            
            self.string_vars[i].trace('w', lambda a, b, c, field_index=i : self.InputChecker(a, b, c, field_index))
        
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(padx=5, pady=5, fill='x')
        ttk.Button(buttonFrame, text='Clear Fields', command=self.ClearFields).pack(side='left')
        ttk.Button(buttonFrame, text='Submit', command=self.BuildValues).pack(side='right')
        ttk.Button(buttonFrame, text='Cancel', command=self.ConfirmCancel).pack(side='right')
    
    # Clears each field of any input by the user (except v_num)
    def ClearFields(self):
        for i in range(1, len(self.string_vars)):
            self.string_vars[i].set('')

    # Obtain a unique ID for v_num
    def GetNewID(self):
        records = self.parent.database.SelectAllRecords()
        id_list = []

        for record in records:
            id_list.append(record[0])
        
        last_id = sorted(id_list)[-1]

        return last_id+1
    
    # Check input for invalid values and prevent them
    def InputChecker(self, a, b, c, field_index):
        current_string = self.string_vars[field_index].get()

        if fields[field_index]['type'] == 'number':
            if not current_string.isnumeric():
                if len(current_string) == 0:
                    return
                if len(current_string) == 1:
                    self.string_vars[field_index].set('')
                    showwarning(title='Warning', message='This field can only contain numbers', parent=self)
                else:
                    self.string_vars[field_index].set(current_string[0:-1])
                    showwarning(title='Warning', message='This field can only contain numbers', parent=self)
    
    # Build a list that will conform to the SQL query structure
    def BuildValues(self):
        self.parent.Log('Building new record values...')
        value_list = []
        
        for i in range(len(self.string_vars)):
            value_list.append(self.string_vars[i].get())
        if value_list[1] == '':
            showwarning(title='Warning', message='VIN is required.', parent=self)
            return
        self.AskAddCancel(value_list)
    
    # Confirm user intent to add the record
    def AskAddCancel(self, values):
        answer = askokcancel(title='Add the record?', message='Click OK to add the vehicle to the database. The Vehicle # and VIN cannot be changed after the record is added.', icon=WARNING, parent=self)
        if answer:
            try:
                result = self.parent.database.AddRecord(values)
                if result == None:
                    showinfo(title='Record added', message='The vehicle was added successfully.')
                    
                    self.parent.PopulateVehicleTable(self.parent.database.SelectAllRecords())
                    self.destroy()
                else:
                    raise DatabaseError
            except DatabaseError:
                showerror(title='Error', message='There was a problem adding the record: ' + str(result) + '.')
    
    # Confirm user intent to cancel form if any of the fields are not empty
    def ConfirmCancel(self):
        all_fields_empty = True
        for i in range(1,len(self.string_vars)):
            if (self.string_vars[i].get() == ''):
                continue
            else:
                all_fields_empty = False
                break
        if all_fields_empty == False:
            answer = askyesno(title='Cancel entry?', message='The field entries will be lost if you cancel. Are you sure you want to cancel?', icon=WARNING, parent=self)
            if answer:
                self.destroy()
        else:
            self.destroy()

#################################################
#| Main Program                                |#
#################################################

if __name__ == '__main__':
    MainAppWindow().Run()