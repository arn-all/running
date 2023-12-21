```
usage: run.py [-h] [--log-dir LOG_DIR] [--artifacts ARTIFACTS [ARTIFACTS ...]] [--symlink-to-artifacts] [--verbose] [--no-persist] ...      
                                                                                                                                            
Run a command with logging and artifact management.                                                                                         
                                                                                                                                            
positional arguments:                                                                                                                       
  command               Command to run with options and arguments                                                                           
                                                                                                                                            
options:                                                                                                                                    
  -h, --help            show this help message and exit                                                                                     
  --log-dir LOG_DIR     Directory for log files                                                                                             
  --artifacts ARTIFACTS [ARTIFACTS ...]                                                                                                     
                        Artifacts to be symlinked or copied                                                                                 
  --symlink-to-artifacts                                                                                                                    
                        Use symlinks instead of copying artifacts                                                                           
  --verbose, -v         Print additional logs to the screen                                                                                 
  --no-persist          Use a temporary workspace                                                                                           

```
