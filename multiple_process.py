"""
from threading import Thread
from main import livestream
from device_listen_ import main

Thread(target = main).start() 
Thread(target = main).start()
Thread(target = livestream).start()



import os                                                                       
from multiprocessing import Pool                                                
                                                                                                                                                                
processes = ('device_listen_.py', 'main.py')                                    
                                                                                                                                  
def run_process(process):                                                             
    os.system('python {}'.format(process))                                       
                                                                                                                                                                
pool = Pool(processes=2)                                                        
pool.map(run_process, processes)   
"""
import os
import asyncio

async def listen():
    path1 = "device_listen_.py"
    os.system('python '+path1)

async def algo():
    path2 = "main.py"
    os.system('python '+path2)

async def main():
   asyncio.gather(listen(),algo())

asyncio.run(main())



