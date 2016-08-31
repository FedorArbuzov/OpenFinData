import shutil
import os
import schedule
import time


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


def delete_cache():
    try:
        # Deleting folders from 1am to 23pm at 24.05 o'clock
        schedule.every().day.at("0:05").do(delete_unnecessary_folders23)
        # Deleting folders from which we created during 24th hour at 1.05 o'clock
        schedule.every().day.at("1:05").do(delete_unnecessary_folders24)

        while 1:
            schedule.run_pending()
            time.sleep(50)
    except Exception as e:
        print("Error: {0}".format(e))

delete_cache()