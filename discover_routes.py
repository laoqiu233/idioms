import pypinyin, mysql.connector
from time import sleep
import multiprocessing as mp
from time import time,sleep

# This script discovers all the routes to the target
# idiom within the configured depth

getHead = lambda idiom: pypinyin.pinyin(idiom, style=pypinyin.Style.TONE3)[0][0][0:-1]
getTail = lambda idiom: pypinyin.pinyin(idiom, style=pypinyin.Style.TONE3)[-1][0][0:-1]
MYSQL_PASSWORD='your_pw_here'

def progress(jobs):
    while not jobs.empty():
        print('{} idioms left'.format(jobs.qsize()))
        sleep(1)

def worker(jobs, tails, MAX_DEPTH):
    db = mysql.connector.connect(host='localhost', port=3306, user='root', passwd=MYSQL_PASSWORD)
    c = db.cursor()
    c.execute('USE idioms')
    while not jobs.empty():
        idiom, path, depth = jobs.get()    
        head = getHead(idiom)
        c.execute('''INSERT INTO `connections` 
                    (`Initial`, `Head`, `Path`, `Depth`) 
                    VALUES 
                    ("{}", "{}", "{}", {})'''.format(head, idiom, '->'.join([idiom] + path), depth)
        )
        db.commit()
        jobs.task_done()
        if depth == MAX_DEPTH - 1 and head in tails:
            c.execute('''INSERT INTO `connections`
                        (`Initial`, `Head`, `Path`, `Depth`)
                        VALUES
                        {}'''.format(','.join(['("{}", "{}", "{}", {})'.format(getHead(i), i, '->'.join([i, idiom] + path), MAX_DEPTH) for i in tails[head]]))
            )
            db.commit()
        elif depth < MAX_DEPTH and head in tails:
            for i in tails[head]:
                jobs.put((i, [idiom] + path, depth + 1))
    c.close()
    db.close()

if __name__ == '__main__':
    # Init and connect db
    db = mysql.connector.connect(host='localhost', port=3306, user='root', passwd=MYSQL_PASSWORD)
    c = db.cursor()
    c.execute('''
    CREATE DATABASE idioms;
    USE idioms;
    CREATE TABLE connections (
        `Id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
        `Initial` CHAR(6) NOT NULL,
        `Head` CHAR(4) NOT NULL,
        `Path` TEXT NOT NULL,
        `Depth` INT UNSIGNED
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;
    SET GLOBAL max_connections = 2000;
    ''')
    c.close()
    db.close()

    # globals
    MAX_DEPTH = 4
    TARGET_IDIOM = '救过不给'
    TARGET = getHead(TARGET_IDIOM)
    heads = {}
    tails = {}

    # Parse the source
    with open('THUOCL_chengyu.txt', 'r', encoding='utf-8') as source:
        idioms = [i for i in map(lambda x: x.split()[0], source.readlines()) if len(i) <= 4]

    # Filter by heads and tails

    for idiom in idioms:
        head = getHead(idiom)
        tail = getTail(idiom)
        if head not in heads:
            heads[head] = [idiom]
        else: 
            heads[head].append(idiom)
        if tail not in tails:
            tails[tail] = [idiom]
        else: 
            tails[tail].append(idiom)

    # Put in initial jobs
    jobs = mp.JoinableQueue()
    if TARGET in tails:
        for idiom in tails[TARGET]: jobs.put((idiom, [TARGET_IDIOM], 1))

    print('Creating processes')
    # Create thread for progress
    process = mp.Process(target=progress, args=(jobs, ), name='Progress')
    process.daemon = True
    process.start()

    # Create threads based on cpu usage
    start = time()
    processes = []
    count = mp.cpu_count()
    for i in range(count):
        process = mp.Process(target=worker, args=(jobs, tails, MAX_DEPTH))
        process.daemon = True
        process.start()
        processes.append(process)

    print('{} processes created.'.format(count))

    jobs.join()
    print('Finished in {} seconds'.format(time() - start))