import schedule
import time
 
def job(t):
    print("Добрый вечер! Встречайте нашу опиздохуительную рассылочку: ", t)
    return
 
schedule.every().hour.at("00:05").do(job, "р а с с ы л о ч к а")
 
while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute
