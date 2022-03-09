import ips
from shutil import rmtree as rmdir
import os
import traceback

from ips.structures import Object, Powerstand

had_error = False

consumers = {
    "houseA",  # дом А
    "houseB",  # дом Б
    "factory",  # больницы
    "hospital",  # заводы
}

generators = {
    "solar",  # солнечные электростанции
    "wind",  # ветровые электростанции
    "TPS",  # теплоэлектростанции
}

stations = {
    "main",  # подстанции
    "miniA",  # мини-подстанции А
    "miniB",  # мини-подстанции Б
}


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
            main()  # try again, why not)
        raise e
    logger.flush()
    if psm.tick == 99:
        logger.next_log()
    # psm.save_and_exit()


class Controller:
    def __init__(self) -> None:
        self.psm = None
        self.addr2obj = {}
        self.type2addrs = {
            "main": [],
            "miniA": [],
            "miniB": [],
            "solar": [],
            "wind": [],
            "houseA": [],
            "houseB": [],
            "factory": [],
            "hospital": [],
            "storage": [],
            "TPS": [],
        }
        self.net2addrs = {}
        self.addr2nets = {}

    def run(self, psm: Powerstand):
        psm.objects[0].path

    def init(self, psm: Powerstand):
        for obj in psm.objects:
            for i in range(len(obj.address)):
                self.addr2obj[obj.address[i]] = obj
                self.type2addrs[obj.type] += [obj.address[i]]
                self.net2addrs[obj.path[i]] += [obj.address[i]]
        for i, net in psm.networks.items():
            if not net.location[0] in self.addr2nets:
                self.addr2nets[net.location[0]] = {}
            self.addr2nets[net.location[0]][net.location[1]] = i


class Module:
    def __init__(self, addr) -> None:
        self.addr = addr  # 'M9'
        self.station = None
        self.lines = [Line(), Line()] if addr[0] == 'm' else \
            [Line(), Line(), Line()]
        self.parent = None
        self.stored = 0
        self.stored_available = 0
        self.storages = 0

    def proceed(self):
        for line in self.lines:
            for ch in line.childs:
                ch.proceed()
            line.calc_delta()

    def do_tree(self, addr2obj: dict[str, Object], net2addrs: dict[int, list[str]], addr2nets: dict[str, dict[int, int]]):
        self.station = addr2obj[self.addr]
        

    def get_delta(self) -> float:
        return self.delta + sum(line.get_delta() for line in self.lines)

    def get_stored(self) -> float:
        return sum(line.get_stored() for line in self.lines)

    def get_storages(self) -> int:
        return sum(line.get_storages() for line in self.lines)


class Line:
    def __init__(self) -> None:
        self.childs: list[Module] = []  # [Module]
        self.objects = []
        self.delta = 0
        self.parent = None
        self.powered = False

    def get_delta(self) -> float:
        x = self.delta + sum(child.get_delta() for child in self.childs)
        return x - abs(x) * min(x * x / 3600, .25)

    def get_stored(self) -> float:
        return

    def get_storages(self) -> int:
        return

    def calc_delta(self):
        self.delta = 0
        self.delta -= sum(map(get_consumption, self.objects))
        self.delta += sum(map(get_generation, self.objects))


def get_consumption(obj: Object) -> float:
    pass


def get_generation(obj: Object) -> float:
    pass


def reset():
    logger.log('reset')
    rmdir('SB', ignore_errors=True)  # sandbox
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
        if os.path.isfile(self.path + f"log-{self.get_num()}.txt"):
            with open(self.path + f"log-{self.get_num()}.txt", 'r') as log_out:
                print(self.path + f"log-{self.get_num()}.txt" + '>>>>>>')
                print(log_out.read())
                print(self.path + f"log-{self.get_num()}.txt" + '<<<<<<')
        next = self.get_num() + 1
        open(self.path + 'log_num.txt', 'w').write(str(next))


logger = Logger('Logs/')

if __name__ == '__main__':
    main()
