import sys
import ips
from shutil import rmtree as rmdir
import os
import traceback

had_error = False

def main():
    psm = ips.init_test()
    if psm.tick == 0:
        reset()
    logger.log(f'--- tick {psm.tick} ---')
    cont = Controller()
    try:
        cont.run(psm)
    except Exception as e:
        logger.log(traceback.format_exc())
        logger.flush()
        reset()
        if not had_error:
            had_error = True
            main() # try again, why not)
        raise e
    logger.flush()
    # psm.save_and_exit()

class Controller:
    def __init__(self) -> None:
        pass

    def run(self, psm):
        pass


def reset():
    logger.log('reset')
    rmdir('SB', ignore_errors=True) # sandbox
    os.mkdir('SB')
    if not os.path.isdir('Logs'):
        os.mkdir('Logs')
    logger.next_log()


class Logger:
    def __init__(self, path) -> None:
        self.buffer = []
        self.path = path

    def log(self, obj):
        self.buffer += [str(obj)]

    def flush(self):
        if not self.buffer:
            return
        with open(self.path + f"log-{self.get_num()}.txt", 'a') as log_out:
            log_out.write('log: ' + '\nlog: '.join(self.buffer) + '\n')
        self.buffer = []
    
    def get_num(self) -> int:
        try:
            return int(open(self.path + 'log_num.txt').read())
        except (FileNotFoundError, ValueError):
            return 0
    
    def next_log(self):
        next = self.get_num() + 1
        open(self.path + 'log_num.txt', 'w').write(str(next))


logger = Logger('Logs/')

if __name__ == '__main__':
    main()
