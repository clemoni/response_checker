from utilities import primary_tools as pt

from time import sleep

from datetime import datetime 

from os import path, environ

from multiprocessing import Queue, Process, Lock, active_children, set_start_method

from multiprocessing import set_start_method

from queue import Empty

import uuid

from sys import exit



def scan_folder(type_scan, queue, folder_path, scan_time=3, timeout=18000, current_size=None, current_ts=None):
    scanner_fn=pt.get_file_object_from_dir if type_scan=='file' else pt.get_folder_object_from_dir
    current_size = len(scanner_fn(folder_path)) if current_size is None else current_size
    current_ts= datetime.now().timestamp() if current_ts is None else current_ts
    
    folder_scan_dict={
        'current_size':current_size,
        'current_ts':current_ts,
        'start_countdown':None
    }
        
    def collect_current_size(folder_path):
        return len(scanner_fn(folder_path))
        
    def collect_new_folder_created():
        folder_collect=scanner_fn(folder_path)
            
        return [folder for folder in folder_collect if path.getctime(folder.path) > folder_scan_dict['current_ts']]
        
        
    def r_get_earliest_ts_from_new_folder(new_folder_list, current_ts, save_list=None, earliest_ts=None):
        save_list=new_folder_list.copy() if save_list is None else save_list
        earliest_ts=current_ts if earliest_ts is None else earliest_ts
    
        if len(save_list)==0:
            return earliest_ts
        else:
            current_folder=save_list.pop(0)
                
            folder_ctime=path.getctime(current_folder.path)
                
            earliest_ts= folder_ctime if earliest_ts < folder_ctime else earliest_ts
                
            return r_get_earliest_ts_from_new_folder(new_folder_list, current_ts, save_list, earliest_ts)
                    
    while True:
         
        new_size=collect_current_size(folder_path)
                
        if new_size > folder_scan_dict['current_size']:
                    
            new_folders_list=collect_new_folder_created()

            for i in new_folders_list:
                 queue.put(i.path)
                    
      
            folder_scan_dict['current_size']=new_size
                    
            folder_scan_dict['current_ts']=r_get_earliest_ts_from_new_folder(new_folders_list, folder_scan_dict['current_ts'])
                    
            folder_scan_dict['start_countdown']=None
           
        
        else:
           
            folder_scan_dict['start_countdown']=datetime.now() if folder_scan_dict['start_countdown'] is None else folder_scan_dict['start_countdown'] 

            time_delta=datetime.now()-folder_scan_dict['start_countdown']

            if time_delta.total_seconds()>timeout:
                queue.put(None)
                break

        sleep(scan_time)
                

def consumer_main_folder(queue):
    print('Consumer main: Running')
    # consume work
    while True:
        subfolder = queue.get()
   
        if subfolder is None:
            break
        else:
            print(f'folder {subfolder}')
            queue_process(subfolder)

        print(f'>got file {subfolder}')

    print('Consumer MAIN: KILLED')
       

def consumer_sub_folder(queue, queue_id):
    print(f'Consumer sub {queue_id}: Running')
    # consume work
    while True:
        file = queue.get()
        
        if file is None:
            break
        else:
            print(f'>got file {file} for {queue_id}')
    # all done
    print(f'Consumer: Done for {queue_id}', flush=True)


def task(lock):
    # acquire the lock
    with lock:
        # block for a moment
        sleep(1)


def queue_process(folder_path):
    
    queue_id=int(uuid.uuid4())

    print(f'New queue processed {queue_id}')

    subfolder_queue=Queue()

    producer_process = Process(target=scan_folder, args=('file', subfolder_queue, folder_path, 3, 60))
    producer_process.start()

    consumer_process = Process(target=consumer_sub_folder, args=(subfolder_queue, queue_id))
    consumer_process.start()

    


if __name__=="__main__":

    set_start_method('fork')
    # create a shared lock
    lock = Lock()

    folder_queue = Queue()

    folder_path="/Users/clement/Downloads/test_picking"

    consumer_process = Process(target=consumer_main_folder, args=(folder_queue, ))
    consumer_process.start()

    producer_process = Process(target=scan_folder, args=('folder', folder_queue, folder_path, 3, 60))
    producer_process.start()

    producer_process.join()
    consumer_process.join()

    active = active_children()
    for child in active:
        child.terminate()

    exit()
