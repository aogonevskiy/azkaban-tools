import os
import time
import datetime
import sys
import shutil
# import optparse
from stat import ST_SIZE, ST_MTIME

jobs_dir = '~/apps/jobs'
logs_dir = '~/apps/logs'
days_to_keep=20
backup_dir = '/tmp/azkaban_backup'
have_files_to_backup=False

def is_execution_file(full_path):
    """ method checks if file is an Azkaban execution file """
    
    if not os.path.isfile(full_path): return False
    
    (name, ext) = os.path.splitext(os.path.split(full_path)[1])
    
    try:
        int(name)
        if ext == '.json': return True
    except ValueError:
        return False
    
    return False

def get_execution_files(exec_dir):
    """ method returns list of execution files (full path) in the specified directory """
    
    # listing all the files
    exec_files = os.listdir(exec_dir)
    
    # filtering execution files
    exec_files = [os.path.join(exec_dir,f) for f in exec_files if is_execution_file(os.path.join(exec_dir,f))]
    
    return exec_files

def init_backup_dirs(root_backup_dir):
    """ Method initializes (creates) backup directories: root backup dir, executions and logs """
    
    d = datetime.datetime.now().strftime('azkaban_backup_%Y%m%d_%H%M%S')
    path = os.path.join(root_backup_dir,d)
    print 'Backup directory = %s' % path
    
    logs_backup_path=os.path.join(path,'logs')
    execs_backup_path=os.path.join(path,'executions')
    print 'Creating logs backup directory = %s' % logs_backup_path
    print 'Creating executions backup directory = %s' % execs_backup_path
    os.makedirs(logs_backup_path)
    os.makedirs(execs_backup_path)
    return (logs_backup_path,execs_backup_path, path)


def backup_old_execution_files(exec_dir, backup_dir, days_to_keep=7):
    """ method moves execution files that are older than <days_to_keep> to the <backup_dir> """

    global have_files_to_backup
    
    exec_files = get_execution_files(exec_dir)
    print '# of files in the executions dir = %d' % len(exec_files)
    
    # getting files older than <days_to_keep>
    old_files = [f for f in exec_files if (time.time() - os.stat(f)[ST_MTIME]) > days_to_keep * 60 * 60 * 24 ]
    
    print '# of old execution files to backup = %d' % len(old_files)
    
    # moving files to backup directory
    for f in old_files:
        print 'Moving %s to %s' % (f,backup_dir)
        shutil.move(f,backup_dir)
        
        have_files_to_backup=True
        
    return None

def backup_empty_execution_files(exec_dir, backup_dir):
    """ method moves zero sized execution files into the <backup_dir> """
    
    global have_files_to_backup
    
    exec_files = get_execution_files(exec_dir)
    print '# of files in the executions dir = %d' % len(exec_files)
    
    # gettign files older than <days_to_keep>
    old_files = [f for f in exec_files if os.stat(f)[ST_SIZE]==0 ]
    
    print '# of empty execution files to backup = %d' % len(old_files)
    
    # moving files to backup directory
    for f in old_files:
        print 'Moving %s to %s' % (f,backup_dir)
        shutil.move(f,backup_dir)
        
        have_files_to_backup=True
        
    return None

def backup_old_log_files(logs_dir, backup_dir):
    
    global have_files_to_backup
    
    # listing all the files
    job_dirs = os.listdir(logs_dir)
    
    # joinng filenames with path
    job_dirs = [os.path.join(logs_dir, f) for f in job_dirs]
    
    # filtering directories
    job_dirs = [os.path.join(logs_dir,f) for f in job_dirs if os.path.isdir(f)]
    print '# of job log directories %s' % len(job_dirs)
    
    for d in job_dirs:
        print 'Procesing %s' % d

        dirs = os.listdir(d)
        
        # filtering old dirs (length, isdir and older than days_to_keep)
        dirs = [os.path.join(d, f) for f in dirs if len(f) == 23 and os.path.isdir(os.path.join(d, f)) and (time.time() - time.mktime(time.strptime(f[0:19], "%m-%d-%Y.%H.%M.%S"))) > days_to_keep * 60 * 60 * 24]
        print 'Found %s old directories' % len(dirs)
        
        # moving files to backup directory
        for f in dirs:
            
            # adding job name to the target_path
            target_path = os.path.join(backup_dir,f.split('/')[-2])
            
            print 'Moving %s to %s' % (f,target_path)
            shutil.move(f,target_path)
            
            have_files_to_backup=True
            
    return None
                

def main():

#    option_parser = optparse.OptionParser()
#    
#    #  p.add_option('--dryRun', '-d') 
#    option_parser.add_option("-d", "--dryRun", action="store_true", dest="dry_run")
#    option_parser.add_option("-l", "--logs", dest="logs_dir", help="Azkaban's logs directory", metavar="LOGS_DIR")
#    option_parser.add_option("-j", "--jobs", dest="jobs_dir", help="Azkaban's jobs directory", metavar="JOBS_DIR")
#    options, arguments = option_parser.parse_args()
    
    if os.name == 'nt':
        print 'Looks like you\'re running Windows OS. Script was not tested in Windows so I better exit. If you still need to run it just comment out OS check'
        sys.exit()
        
    if not os.path.exists(backup_dir): 
        print 'ERROR -- Backup directory does not exist: %s' % backup_dir
        sys.exit()
    
    paths = init_backup_dirs(backup_dir)

    global jobs_dir
    """ AS SOON AS YOU WRITE TO A VARIABLE, that variable is AUTOMATICALLY considered LOCAL to the function block in which its declared."""        
    jobs_dir = os.path.expanduser(jobs_dir)
    print 'Jobs dir = %s' % jobs_dir

    global logs_dir
    logs_dir = os.path.expanduser(logs_dir)
    print 'Logs dir = %s' % logs_dir
        
    exec_dir = os.path.join(jobs_dir, 'executions')
    print 'Executions dir = %s' % exec_dir
    
    print '*** Backing up old execution files - begin ***'
    backup_old_execution_files(exec_dir, paths[1])
    print '*** Backing up old execution files - end ***'
    
    print '*** Backing up empty execution files - begin ***'
    backup_empty_execution_files(exec_dir, paths[1])
    print '*** Backing up empty execution files - end ***'
    
    print '*** Backing up old log files - begin ***'
    backup_old_log_files(logs_dir, paths[0])
    print '*** Backing up old log files - end ***'
    
    if not have_files_to_backup:
        print 'Nothing was backed up - removing backup dir = %s' % paths[2] 
        shutil.rmtree(paths[2])
        
# Running

if __name__ == '__main__':
    main()
#    print is_execution_file('/Users/aogonevskiy/apps/jobs/executions/1.json')
#    print is_execution_file('/Users/aogonevskiy/apps/jobs/executions/1.exe')
#    print is_execution_file('/Users/aogonevskiy/apps/jobs/executions/A123.json')
