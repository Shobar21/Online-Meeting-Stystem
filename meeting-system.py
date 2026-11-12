import tkinter as tk
import sqlite3
import re
import csv
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime



root = tk.Tk()
root.title("Online Meeting Management System")
root.geometry("400x300")
root.configure(bg="#255252")

# login in
loginFrame = tk.Frame(root,bg="#f4f4f4", borderwidth=3,  relief="groove", padx=20, pady=20)
loginFrame.pack(pady=20)

titleLabel = tk.Label(loginFrame,text="OMMS Login", font=("Arial",16,"bold"),bg="#f4f4f4",fg="black")
titleLabel.grid(row=0, column=0, columnspan=2, pady=(0,15))

usernameLabel = tk.Label(loginFrame,text="Username: ", font=("Arial",11),bg="#f4f4f4",fg="#333333")
usernameLabel.grid(row=1, column=0, sticky="e",pady=5)

usernameEntry = tk.Entry(loginFrame, width=22)
usernameEntry.grid(row=1,column=1,pady=5)

passwordLabel = tk.Label(loginFrame,text="Password: ",font=("Arial",11),bg="#f4f4f4",fg="#333333")
passwordLabel.grid(row=2,column=0,sticky="e",pady=5)

passwordEntry = tk.Entry(loginFrame, width=22, show="*")
passwordEntry.grid(row=2,column=1,pady=5)


# function for login
def loginClicked():
    username = usernameEntry.get()
    password = passwordEntry.get()
    conn = sqlite3.connect("omms.db")
    cursor = conn.cursor()

    cursor.execute("""
SELECT * FROM USERS WHERE username = ? AND password = ?
    """, (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        userRole = result[3]  # host in 4th column
        messagebox.showinfo("Login Success", f"Welcome,{userRole}")
        root.destroy()
        openDashboard(username,userRole)
    else:
       messagebox.showerror("Login Failed", "Invalid username or password")


# create meetings
def openCreateMeeting(username,refreshCallback, meeting_id=None, existingData=None):
    meetingWin = tk.Toplevel()
    meetingWin.title("Update Meeting" if meeting_id else "Create Meeting")
    meetingWin.geometry("400x450")
    meetingWin.configure(bg="#1e2a38")

    tk.Label(meetingWin, text="Meeting Info", font=("Arial", 13 , "bold"), bg="#1e2a38", fg="white").pack(pady=(15,10))

    tk.Label(meetingWin, text="Title: ", bg="#1e2a38", fg="white").pack(anchor="w",padx=20)
    titleEntry = tk.Entry(meetingWin,width=35)
    titleEntry.pack(padx=20)

    tk.Label(meetingWin, text="Date (YYYY-MM-DD): ",bg="#1e2a38", fg="white").pack(anchor="w", padx=20,pady=(10,0))
    dateEntry = tk.Entry(meetingWin,width=35)
    dateEntry.pack(padx=20)

    tk.Label(meetingWin, text="Time (HH:MM): ",bg="#1e2a38", fg="white").pack(anchor="w", padx=20,pady=(10,0))
    timeEntry = tk.Entry(meetingWin,width=35)
    timeEntry.pack(padx=20)

    tk.Label(meetingWin, text="Duration: ", bg="#1e2a38", fg="white").pack(anchor="w", padx=20,pady=(10,0))
    durationEntry = tk.Entry(meetingWin,width=35)
    durationEntry.pack(padx=20)

    tk.Label(meetingWin, text="Agenda: ", bg="#1e2a38", fg="white").pack(anchor="w", padx=20,pady=(10,0))
    agendaText = tk.Text(meetingWin, width=35, height=5)
    agendaText.pack(padx=20)

    # if editing prefill the fields
    if existingData:
        titleEntry.insert(0,existingData[1])
        dateEntry.insert(0, existingData[2])
        timeEntry.insert(0, existingData[3])
        durationEntry.insert(0, existingData[4])

        conn = sqlite3.connect("omms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT agenda FROM meetings WHERE id = ?", (meeting_id,))
        agendaResult = cursor.fetchone()
        conn.close()
        if agendaResult and agendaResult[0]:
            agendaText.insert("1.0", agendaResult[0])

    def saveMeeting():
        title = titleEntry.get()
        date = dateEntry.get()
        time = timeEntry.get()
        duration = durationEntry.get()
        agenda = agendaText.get("1.0", "end").strip()

        if not title or not date or not time:
            messagebox.showerror("Missing Info", "Title, Date, and time are required.")
            return

        conn = sqlite3.connect("omms.db")
        cursor = conn.cursor()

        if meeting_id:
            # update existing meeting
            cursor.execute("""
                UPDATE meetings 
                SET title = ?, date = ?, time = ?, duration = ?, agenda = ?
                WHERE id = ?
            """, (title, date, time, duration, agenda, meeting_id))

            successMsg = "Meeting Update Successfully!"

        else:
            cursor.execute("""
                INSERT INTO meetings (title, date, time, duration, agenda, host)
                VALUES(?, ?, ?, ?, ?, ?)
             """, (title, date, time, duration, agenda, username))

            successMsg = "Meeting Saved Successfully!"
        conn.commit()
        conn.close()
        messagebox.showinfo("Saved", successMsg)

        meetingWin.destroy()
        refreshCallback()
    saveButton = tk.Button(meetingWin, text="Save", command=saveMeeting, bg="#2e8b8b", fg="white", width=10, activebackground="#256d6d")
    saveButton.pack(pady=15)

def cleanDuplicate():
    conn = sqlite3.connect("omms.db")
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM meetings
    WHERE id NOT IN(
    SELECT MIN(id)
    FROM meetings
    GROUP BY title, date , time, duration, agenda, host)
    """)
    conn.commit()
    conn.close()
cleanDuplicate()


# dashboard 
def openDashboard(username,role):
    dashboard = tk.Tk()
    dashboard.title("Online Meeting Management System")
    dashboard.geometry("900x600")
    dashboard.configure(bg="#255252")

# header
    welcomeLabel = tk.Label(dashboard, text=f"Welcome {username} ({role})", font=("Arial", 14,"bold"), bg="#1e2a38", fg="white")
    welcomeLabel.pack(pady=15)

# navigation bar
    navFrame = tk.Frame(dashboard,bg="#2e8b8b")
    navFrame.pack(fill="x")

# content area
    contentTitle = tk.Label(dashboard, text="Upcoming Meetings", font=("Arial", 12,"bold"), bg="#1e2a38", fg="white")
    contentTitle.pack(pady=10)

#table for meetings
    columns = ("id","Title","Date","Time","Duration")
    meetingTable = ttk.Treeview(dashboard, columns=columns, show="headings",height=15)

    meetingTable.heading("id", text="ID")
    meetingTable.column("id", width=0, stretch=False) #hidden column
    for col in ("Title", "Date", "Time", "Duration"):
        meetingTable.heading(col, text=col)
        meetingTable.column(col, width=150)
    meetingTable.pack(padx=20,pady=10,fill="x")

# load meetings from database and display them
    def loadMeetings():
        # clear all existing rows first
        for row in meetingTable.get_children():
            meetingTable.delete(row)
        conn = sqlite3.connect("omms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, date, time, duration FROM meetings ")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            meetingTable.insert("","end",values=row)
    loadMeetings()
 
# Buttons for editing and delect meeting
    actionFrame = tk.Frame(dashboard, bg="#1e2a38")
    actionFrame.pack(pady=5)

    if role in ("host", "admin"):
          editBtn = tk.Button(actionFrame, text="Edit", bg="#2e8b8b", fg="white",activebackground="#256d6d", width=15, command=lambda: editSelected() )
          editBtn.pack(side="left",padx=5)
          cancelBtn = tk.Button(actionFrame, text="Cancel", bg="#b03a3a", fg="white",activebackground="#8c2e2e", width=15,command=lambda: cancelSelected())
          cancelBtn.pack(side="left",padx=5)

# reminder message
    def checkReminder():
        conn = sqlite3.connect("omms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, date, time FROM meetings")
        rows = cursor.fetchall()
        conn.close()

        now = datetime.now()
        # print("Current time", now)
        upcoming = []

        possibleFormates = ["%Y-%m-%d %I:%M %p", "%Y-%m-%d %I:%M%p" ]

        for title, date, time in rows:
            timeClean = time.strip()
            meetingDt = None

            for fmt in possibleFormates:
                try:
                     meetingDt = datetime.strptime(f"{date} {timeClean}", fmt )
                     break
                except ValueError as e:
                   print("Failed to parse: ",e)
                   continue
            if meetingDt is None:
                continue

            diffMinutes = (meetingDt - now).total_seconds() / 60
            # print("Difference in minutes:", diffMinutes)
            if 0 <= diffMinutes <= 60:
                upcoming.append(f"{title} starts at {time}")

        if upcoming:
            message = "\n".join(upcoming)
            messagebox.showinfo("Meeting Reminder", message)
        else:
            messagebox.showinfo("Meeting Reminder", "No meetings starting in the next hour.")

    reminderBtn = tk.Button(actionFrame, text="Check Reminders", bg="#8b6b3a", fg="white", activebackground="#6e5426", command=checkReminder)
    reminderBtn.pack(pady=5)

# meeting notes
    def openNotesWindow():
        nw = tk.Toplevel()
        nw.title("Meeting Notes")
        nw.geometry("600x500")
        nw.configure(bg="#1e2a38")

        tk.Label(nw, text="Enter Meeting ID to View/Add Notes:", font=("Arial", 11, "bold"),bg="#1e2a38", fg="white").pack(pady=(15,5))


        idEntry = tk.Entry(nw, width=15)
        idEntry.pack()

        currentMeetingID = {"value": None}

        notesText = tk.Text(nw, width=65, height=8)

        historyTable = ttk.Treeview(nw, columns=("id","Meeting","Content"),show="headings", height=8)
        historyTable.heading("id", text="ID")
        historyTable.column("id", width=60)
        historyTable.heading("Meeting", text="Meeting")
        historyTable.column("Meeting", width=150)
        historyTable.heading("Content", text="Content")
        historyTable.column("Content", width=350)

        def refreshHistory():
            for row in historyTable.get_children():
                historyTable.delete(row)

            if currentMeetingID["value"] is None:
                return
            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute(""" 
            SELECT notes.id, meetings.title, notes.content From notes
             JOIN meetings ON notes.meeting_id = meetings.id
             ORDER BY notes.id
            """)
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                historyTable.insert("","end", values=row)

        def loadNotes():
            midText = idEntry.get().strip()
            if not midText.isdigit():
                messagebox.showerror("Invaild ID", "Please enter a valid numeric Meeting ID.")
                return

            mid = int(midText)
            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM meetings WHERE id = ?",(mid,))
            exists = cursor.fetchone()
            conn.close()

            if not exists:
                messagebox.showerror("Not found", f"No meeting found with ID {mid}")
                return
            
            currentMeetingID["value"] = mid
            print("Loaded meeting ID successfully:",currentMeetingID["value"])
            notesText.delete("1.0","end")
            refreshHistory()

        loadBtn = tk.Button(nw, text="Load Notes", bg="#2e8b8b", fg="white", activebackground="#256d6d", command=loadNotes)
        loadBtn.pack(pady=(0, 10))
        notesText.pack(padx=15, pady=5)

        def saveNotes():
            # print("Attempting to save. Current meeting id is:", currentMeetingID["value"])
            if currentMeetingID["value"] is None:
                messagebox.showerror("No meeting loaded", "Please load a meeting ID first.")
                return

            content = notesText.get("1.0","end").strip()
            if not content:
                messagebox.showerror("Empty Note", "Please write a note before saving.")
                return
            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (meeting_id, content) VALUES (?, ?)",(currentMeetingID["value"], content))
            conn.commit()
            conn.close()

            notesText.delete("1.0", "end")
            refreshHistory()

        saveBtn = tk.Button(nw, text="Save Note", bg="#2e8b8b", fg="white", activebackground="#256d6d", command=saveNotes)
        saveBtn.pack(pady=5)

        historyTable.pack(padx=15, pady=10, fill="both", expand=True)
        refreshHistory()

# searching meeting
    def openSearchWindow():
        sw= tk.Toplevel()
        sw.title("Search Meetings")
        sw.geometry("1200x450")
        sw.configure(bg="#1e2a38")

        createMeetingbtn = tk.Button(sw, text="Create Meeting", bg="#2e8b8b", fg="white",
        activebackground="#256d6d", command= lambda: openCreateMeeting(username, loadMeetings))
        createMeetingbtn.pack(padx=5, pady=5)

        searchFrame = tk.Frame(sw, bg="#1e2a38")
        searchFrame.pack(pady=15)

        tk.Label(searchFrame, text="Title:",bg="#1e2a38", fg="white").grid(row=0, column=0, padx=5)
        titleSearch = tk.Entry(searchFrame, width=15)
        titleSearch.grid(row=0, column=1, padx=5)

        tk.Label(searchFrame, text="Host:",bg="#1e2a38", fg="white").grid(row=0, column=2, padx=5)
        hostSearch =tk.Entry(searchFrame, width=15)
        hostSearch.grid(row=0, column=3,padx=5)

        tk.Label(searchFrame, text="Date:",bg="#1e2a38", fg="white").grid(row=0, column=4, padx=5)
        dateSearch =tk.Entry(searchFrame, width=15)
        dateSearch.grid(row=0, column=5, padx=5)

        columns = ("ID", "Title", "Host", "Date", "Time", "Duration", "Agenda", "Notes")
        rstTable = ttk.Treeview(sw, columns=columns, show="headings", height=21)
        for col in columns:
            rstTable.heading(col, text=col)
            rstTable.column(col, width=110)
        rstTable.pack(padx=15, pady=15, fill="both", expand=True)

        def getNoteSum(meeting_id):
            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM notes WHERE meeting_id = ?", (meeting_id,))
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                return "No Notes"
            return "; ".join(row[0] for row in rows)

        def runSearch():
            for row in rstTable.get_children():
                rstTable.delete(row)

            titleValue = titleSearch.get().strip()
            hostValue = hostSearch.get().strip()
            dateValue = dateSearch.get().strip()

            query = "SELECT id, title, host, date, time, duration, agenda FROM meetings Where 1=1"
            params = []

            if titleValue:
                query +=" AND title LIKE ?"
                params.append(f"%{titleValue}%")
            if hostValue:
                query += " AND host LIKE ?"
                params.append(f"%{hostValue}%")
            if dateValue:
                query += " AND date LIKE ?"
                params.append(f"%{dateValue}%")

            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute(query, params)
            # print("Query: ", query)
            # print("Params: ", params)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                meeting_id = row[0]
                notesSummary = getNoteSum(meeting_id)
                fullRow = list(row) + [notesSummary]
                rstTable.insert("","end", values=fullRow)

        srchBtn = tk.Button(searchFrame, text="Search", bg="#2e8b8b", fg="white", activebackground="#256d6d", command=runSearch)
        srchBtn.grid(row=0, column=6, padx=10)
        runSearch()

# backup and restore data
    def openBackupWindow():
         bw = tk.Toplevel()
         bw.title("Backup/Restore")
         bw.geometry("300x200")
         bw.configure(bg="#1e2a38")

         def backupData():
            filePath = filedialog.asksaveasfile(
              defaultextension=".csv",
              filetypes=[("CSV files", "*.csv")],
              title="Save Backup As"
          )
            if not filePath:
              return
            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, date, time, duration, agenda, host FROM meetings")
            rows = cursor.fetchall()
            conn.close()

            # with open(filePath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(filePath)
            writer.writerow(["id","title","date","time","duration","agenda","host"])
            writer.writerows(rows)
            filePath.close()

            messagebox.showinfo("Backup", "Data exported successfully.")
 
         # restoredata
         def restoreData():
           filePath = filedialog.askopenfilename(
              filetypes=[("CSV files", "*.csv"),("All files","*.*")],
              title="Select Backup Files"
            )
           if not filePath:
            return

           confirm = messagebox.askyesno("Confirm Restore", "This will add the backup's meetings to your database. Continue?")

           if not confirm:
            return

           conn = sqlite3.connect("omms.db")
           cursor = conn.cursor()

        #    clear existing meetings to pervent duplicate row
           cursor.execute("DELETE FROM meetings")

           # reset Sqlite ID auto
           cursor.execute("DELETE FROM sqlite_sequence WHERE name='meetings'")


           with open(filePath, "r", newline="", encoding="utf-8") as f:
              reader = csv.reader(f)
              next(reader, None) #skip header row
              for row in reader:
                  if not row or len(row)<7:
                      continue
                  
                  _,title, date, time, duration, agenda, host = row
                  cursor.execute("""
                    INSERT INTO meetings (title, date, time, duration, agenda, host)
                    VALUES(?,?,?,?,?,?)
                """,(title, date, time, duration, agenda, host))
           conn.commit()
           conn.close()

           messagebox.showinfo("Restore", "Data Restore successfully.")
           if "loadMeetings" in globals():
              loadMeetings()

         backupBtn = tk.Button(bw, text="Backup Data", bg="#2e8b8b", fg="white",
                           activebackground="#256d6d" , width=15, command=backupData)
         backupBtn.pack(pady=15)

         restoreBtn = tk.Button(bw, text="Restore Data", bg="#2e8b8b", fg="white",
                           activebackground="#256d6d" , width=15, command=restoreData)
         restoreBtn.pack(pady=15)

            
    def getSelectedMeeting():
        selected = meetingTable.selection()
        if not selected:
            messagebox.showwarning("NO Selection", "Please select a meeting first")
            return None
        return meetingTable.item(selected[0])["values"] #returns (id, title, date, time, duration)

    def editSelected():
        meetingData = getSelectedMeeting()
        if meetingData:
            meeting_id = meetingData[0]
            openCreateMeeting(username, loadMeetings, meeting_id=meeting_id, existingData=meetingData)
            # print("Editing meeting:", meetingData)

    def cancelSelected():
        meetingData = getSelectedMeeting()
        if meetingData:
            meeting_id = meetingData[0]
            meeting_title = meetingData[1]
            confirm = messagebox.askyesno("Confirm Cancel", f"Cancel meeting {meeting_title} ?")
            if confirm:
                conn = sqlite3.connect("omms.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM meetings WHERE id = ?",(meeting_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Cancelled", "Meeting Cancelled Successfully!")
                loadMeetings()
            # print("Canceling meeting:", meetingData)

# participant
    def openParticipantsWindow():
        meetingData = getSelectedMeeting()
        if not meetingData:
            return
        meeting_id = meetingData[0]
        meeting_title = meetingData[1]

        pw = tk.Toplevel()
        pw.title(f"Participants - {meeting_title}")
        pw.geometry("700x250")
        pw.configure(bg="#1e2a38")

        # outer frame to hold listbox 
        topFrame = tk.Frame(pw,bg="#1e2a38")
        topFrame.pack(padx=15, pady=15)

        participantListbox = tk.Listbox(topFrame, width=90, height=10,exportselection=False)
        participantListbox.pack(side="left")

        controlsFrame = tk.Frame(topFrame, bg="#1e2a38")
        controlsFrame.pack(side="left",padx=10)

        emailEntry = tk.Entry(controlsFrame, width=20)
        emailEntry.pack(pady=(0,5))

        def refreshList():
            participantListbox.delete(0, tk.END)
            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, status FROM participants WHERE meeting_id = ?", (meeting_id,))
            rows = cursor.fetchall()
            for row in rows:
                participantListbox.insert(tk.END, f"{row[1]} ({row[2]} [id:{row[0]}])")
            conn.close()

        def addParticipant():
            email = emailEntry.get().strip()
            if not email:
              messagebox.showerror("Missing Email", "Enter a participant email.")
              return
            conn = sqlite3.connect("omms.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO participants (meeting_id, email) VALUES (?, ?) ", (meeting_id, email))
            conn.commit()
            conn.close()
            emailEntry.delete(0,tk.END)
            refreshList()
        def getSelectedParticipantID():
            selection = participantListbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Select a participant first. ")
                return None
            selectedText = participantListbox.get(selection[0])
            # extract id from the text
            match = re.search(r'id:(\d+)', selectedText)
            if match:
                return int(match.group(1))
            return None
        
        def removeSelected():
            pid = getSelectedParticipantID()
            if pid:
                conn = sqlite3.connect("omms.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM participants WHERE id = ?", (pid,))
                conn.commit()
                conn.close()
                refreshList()

        def setStatus(newStatus):
            pid = getSelectedParticipantID()
            if pid:
                conn = sqlite3.connect("omms.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE participants SET status = ? WHERE id = ?",(newStatus, pid))
                conn.commit()
                conn.close()
                refreshList()

        addBtn = tk.Button(controlsFrame, text="Add Participant", width=16, bg="#2e8b8b", fg="white", command=addParticipant)
        addBtn.pack(pady=3)

        removeBtn = tk.Button(controlsFrame, text="Remove Selected", width=16, bg="#b03a3a", fg="white", command=removeSelected)
        removeBtn.pack(pady=3)

        confirmBtn = tk.Button(controlsFrame, text="Confirm", width=16, bg="#3a8b3a", fg="white", command=lambda: setStatus("Confirmed"))
        confirmBtn.pack(pady=3)

        declineBtn = tk.Button(controlsFrame, text="Decline", width=16, bg="#8b6b3a", fg="white", command=lambda: setStatus("Declined"))
        declineBtn.pack(pady=3)

        saveCloseBtn = tk.Button(pw, text="save", width=12, bg="#2e8b8b", fg="white", command=pw.destroy)
        saveCloseBtn.pack(pady=10)

        refreshList()

# Navigation bar last
    tabNames = ["Dashboard", "Meetings", "Participants", "Meeting Notes", "Backup/Restore"]
    for name in tabNames:
        if name == "Meetings":
            if role in ("host","admin"):
             tabButton = tk.Button(navFrame, text=name, bg="#2e8b8b", fg="white", relief="flat", padx=10, pady=5, activebackground="#256d6d", command=openSearchWindow)
            else:
              tabButton = tk.Button(navFrame, text=name, bg="#555555", fg="#aaaaaa",relief="flat", padx=10, pady=5, command=lambda: messagebox.showwarning("Access Denied","Only hosts or admins can manage meetings."))
        elif name == "Participants":
              if role in ("host","admin"):
                 tabButton = tk.Button(navFrame, text=name, bg="#2e8b8b", fg="white", relief="flat", padx=10, pady=5, activebackground="#256d6d", command=openParticipantsWindow)
              else:
                 tabButton = tk.Button(navFrame, text=name, bg="#555555", fg="#aaaaaa",relief="flat", padx=10, pady=5, command=lambda: messagebox.showwarning("Access Denied","Only hosts or admins can manage meetings."))
        elif name =="Meeting Notes":
             tabButton = tk.Button(navFrame, text=name, bg="#2e8b8b", fg="white", relief="flat", padx=10, pady=5, activebackground="#256d6d", command=openNotesWindow)    
        elif name =="Backup/Restore":
             tabButton = tk.Button(navFrame, text=name, bg="#2e8b8b", fg="white", relief="flat", padx=10, pady=5, activebackground="#256d6d", command=openBackupWindow) 
        else:
          tabButton = tk.Button(navFrame, text=name, bg="#2e8b8b", fg="white", relief="flat", padx=10, pady=5, activebackground="#256d6d")
        tabButton.pack(side="left")

    dashboard.mainloop()


loginBtn = tk.Button(loginFrame,text="Login", font=("Arial",11),command=loginClicked, width=10,
                         bg="#294A70",fg="white",activebackground="#1E518B")
loginBtn.grid(row=3, column=0, columnspan=2,pady=15)

root.mainloop()