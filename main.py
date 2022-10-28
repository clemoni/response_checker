from utilities import primary_tools as pt

from time import sleep

from datetime import datetime 

from os import path, environ

# import argparse


# def get_arguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("folder path",
#                         type=str,
#                         help="folder to watch")

#     args= parser.parse_args()

#     return args.number_participants




def init_folder_scan(folder_path, scan_time=3, current_size=None, current_ts=None,):
    current_size = len(pt.get_folder_object_from_dir(folder_path)) if current_size is None else current_size
    current_ts= datetime.now().timestamp() if current_ts is None else current_ts
    
    folder_scan_dict={
        'current_size':current_size,
        'current_ts':current_ts
    }
    
    def wrapper(fn):
        
        def collect_current_size(folder_path):
            
            return len(pt.get_folder_object_from_dir(folder_path))
        
        def collect_new_folder_created():
            folder_collect=pt.get_folder_object_from_dir(folder_path)
            
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
            
        
        def scan_new_folder():
            
            while True:
                
                print('new_loop')
                
                new_size=collect_current_size(folder_path)
                
                if new_size > folder_scan_dict['current_size']:
                    
                    new_folders_list=collect_new_folder_created()
                    
                    print(new_folders_list)
                    
                    folder_scan_dict['current_size']=new_size
                    
                    folder_scan_dict['current_ts']=r_get_earliest_ts_from_new_folder(new_folders_list, folder_scan_dict['current_ts'])
                    
                sleep(scan_time)
                
        def get_current_size(): return folder_scan_dict['current_size']
        
        def get_current_ts(): return folder_scan_dict['current_ts']
        
        return {
            "get_current_size":get_current_size,
            "get_current_ts":get_current_ts,
            "scan_new_folder":scan_new_folder
            
        }.get(fn)
            
    return wrapper

if __name__=="__main__":
    
    print('init')
    
    folder_scan=init_folder_scan('/src')
    
    folder_scan('scan_new_folder')()