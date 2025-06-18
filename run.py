import multiprocessing #Enables the program to run multiple tasks (processes) simultaneously.


def startSherlock():
    print ("Process 1 Starting...")
    from main import start #Imports the start() function from main.py.
    start()#Calls start() to begin the Sherlock assistant process (e.g., launching Eel interface).
    
def listenHotword():
    print ("Process 2 Starting...")
    from backend.feature import hotword #Imports the hotword() function from your assistant's backend.feature module.
    hotword()
    
if __name__ == "__main__": #Ensures the multiprocessing code runs only when the script is executed directly — prevents issues when using multiprocessing on Windows.
    process1 = multiprocessing.Process(target=startSherlock)#process1: will run startSherlock
    process2 = multiprocessing.Process(target=listenHotword) #process2: will run listenHotword

    process1.start() #Starts both processes in parallel.
    process2.start()
    process1.join() #Main script waits for process1 to complete.The join() method blocks further code execution until Sherlock finishes.


    
    if process2.is_alive():#If the hotword process is still running after Sherlock finishes:
        process2.terminate() #It will be forcefully terminated using terminate().
        print("Process 2 terminated.") 
        process2.join() #Then join() is called to properly close it and release system resources.
        
    print("System is terminated.") #Indicates that both processes have exited, and the system has shut down.