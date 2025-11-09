# Cyber-Security-Task4
Task-04 Simple Keylogger
### 🧩 Description  
This project is a **Simple Keylogger** created in Python for **educational and ethical purposes only**.  
The tool records and logs the keys pressed by the user **only while the application window is active**, and saves the keystrokes to a file.  

It helps understand how **key event handling and file logging** work in Python, emphasizing **user consent and transparency** at every step.

### ⚙️ Working Principle  
1. The user launches the application.  
2. On clicking **Start Logging**, the program begins to record keystrokes typed within the focused window.  
3. Logged keys are shown in a **live preview panel** inside the app.  
4. The user can choose a file to save logs or stop logging anytime.  
5. On **Stop Logging**, all recorded keys are safely stored in the selected text file.  

### 💡 Features  
- Records keystrokes only when the app is active (for demo/learning).  
- Option to **start**, **stop**, **save**, and **clear** logs easily.  
- Transparent preview window showing all recorded keys.  
- Saves logs to a `.txt` file chosen by the user.  
- Includes consent and warning messages for ethical use.

### 🧠 Learning Outcomes  
- Handling keyboard events in Python GUI.  
- Logging and saving real-time user inputs.  
- Understanding ethical implications of keylogging tools.

**Example Output**
--- Logging started at 2025-11-09 15:10:25 ---
CHAR('S') keysym=s
CHAR('n') keysym=n
CHAR('e') keysym=e
CHAR('h') keysym=h
CHAR('a') keysym=a
CHAR('l') keysym=l
CHAR('@') keysym=@
CHAR('1') keysym=1
CHAR('2') keysym=2
CHAR('3') keysym=3
--- Logging stopped at 2025-11-09 15:12:02 ---
