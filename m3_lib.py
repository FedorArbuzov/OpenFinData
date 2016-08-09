import schedule
import time
import shutil
import os


# TODO: перенести в m1_main
def delete_unnecessary_folders23():
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
    directories = list(filter(lambda elem: os.path.isdir(elem), os.listdir()))
    for folder in directories:
        if folder.startswith('tmp24'):
            shutil.rmtree(folder)


# Deleting folders from 1am to 23pm at 24.05 o'clock
schedule.every().day.at("18:26").do(delete_unnecessary_folders23)
# Deleting folders from which we created during 24th hour at 1.05 o'clock
schedule.every().day.at("01:05").do(delete_unnecessary_folders24)

while True:
    schedule.run_pending()
    time.sleep(1)

