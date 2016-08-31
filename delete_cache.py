import shutil
import os
import schedule
from time import gmtime, strftime, sleep


def delete_unnecessary_folders23():
    """Deleting all tmp folders which were created between 1 and 24 o'clock"""
    prefixes = ('tmp1', 'tmp2', 'tmp3', 'tmp4', 'tmp5', 'tmp6', 'tmp7',
                'tmp8', 'tmp9', 'tmp10', 'tmp11', 'tmp12', 'tmp13', 'tmp14',
                'tmp15', 'tmp16', 'tmp17', 'tmp18', 'tmp19', 'tmp20', 'tmp21',
                'tmp22', 'tmp23')
    directories = list(filter(lambda elem: os.path.isdir(elem), os.listdir()))
    for folder in directories:
        beginning = str(folder).split('_')[0]
        if beginning in prefixes:
            shutil.rmtree(folder)


def delete_unnecessary_folders24():
    """Deleting all tmp folders which were created during 24th hour of day"""
    directories = list(filter(lambda elem: os.path.isdir(elem), os.listdir()))
    for folder in directories:
        if folder.startswith('tmp0'):
            shutil.rmtree(folder)


def delete_cache(first_time='0:05', second_time='1:05'):
    try:
        # Deleting folders from 1am to 23pm at 24.05 o'clock
        schedule.every().day.at(first_time).do(delete_unnecessary_folders23)
        # Deleting folders from which we created during 24th hour at 1.05 o'clock
        schedule.every().day.at(second_time).do(delete_unnecessary_folders24)

        while 1:
            schedule.run_pending()
            sleep(50)
    except Exception as e:
        print("{0} Error: {1}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), e))
        schedule.clear()
        print('Notification: Timer is reset')
        delete_cache()


delete_cache()
