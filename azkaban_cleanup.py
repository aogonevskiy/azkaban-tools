import os
import time
import datetime
import sys
import shutil
from stat import *

jobs_dir = '~/apps/jobs'
days_to_keep=7
backup_dir = '/tmp/azkaban_backup'

def is_execution_file(full_path):
  """ method checks if file is an Azkaban execution file """

  if not os.path.isfile(full_path): return False

  (name, ext) = os.path.splitext(os.path.split(full_path)[1])

  try:
    int(name)
    if ext == '.json': return True
  except ValueEror:
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
  return (logs_backup_path,execs_backup_path)


def backup_old_execution_files(exec_dir, backup_dir, days_to_keep=7):
  """ method moves execution files that are older than <days_to_keep> to the <backup_dir> """
  
  exec_files = get_execution_files(exec_dir)
  print '# of files in the executions dir = %d' % len(exec_files)

  # getting files older than <days_to_keep>
  old_files = [f for f in exec_files if (time.time() - os.stat(f)[ST_MTIME]) > days_to_keep * 60 * 60 * 24 ]

  print '# of old execution files to backup = %d' % len(old_files)

  # moving files to backup directory
  for f in old_files:
    print 'Moving %s to %s' % (f,backup_dir)
    shutil.move(f,backup_dir)

################################
## Backup empty execution files
################################
def backup_empty_execution_files(exec_dir, backup_dir):
  """ method moves zero sized execution files into the <backup_dir> """
  exec_files = get_execution_files(exec_dir)
  print '# of files in the executions dir = %d' % len(exec_files)

  # gettign files older than <days_to_keep>
  old_files = [f for f in exec_files if os.stat(f)[ST_SIZE]==0 ]

  print '# of empty execution files to backup = %d' % len(old_files)

  # moving files to backup directory
  for f in old_files:
    print 'Moving %s to %s' % (f,backup_dir)
    shutil.move(f,backup_dir)
  return None


################################
## Running
################################
if not os.path.exists(backup_dir): 
  print 'ERROR -- Backup directory does not exist: %s' % backup_dir
  sys.exit()

paths = init_backup_dirs(backup_dir)

jobs_dir = os.path.expanduser(jobs_dir)
print 'Jobs dir = %s' % jobs_dir

exec_dir = os.path.join(jobs_dir, 'executions')
print 'Executions dir = %s' % exec_dir

print '*** Backing up old execution files - begin ***'
backup_old_execution_files(exec_dir, paths[1])
print '*** Backing up old execution files - end ***'

print '*** Backing up empty execution files - begin ***'
backup_empty_execution_files(exec_dir, paths[1])
print '*** Backing up empty execution files - end ***'

# testing
if __name__ == '__main__':
  print is_execution_file('/Users/aogonevskiy/apps/jobs/executions/1.json')
  print is_execution_file('/Users/aogonevskiy/apps/jobs/executions/1.exe')
  print is_execution_file('/Users/aogonevskiy/apps/jobs/executions/A123.json')
