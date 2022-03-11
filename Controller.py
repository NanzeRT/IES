import ips
from shutil import rmtree as rmdir
import os
import traceback

from ips.structures import Object, Powerstand

sunny_lines_raw = set(()) # set((('M9', 1),))
subsunny_lines_raw = set()
sunny_lines = set()
subsunny_lines = set()
sun_level = 6
presun_repair_shift = 2

BUY_ADD = 2
SELL_ADD = 2

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

type2letter = {
    "main" : "M",
    "miniA" : "e",
    "miniB" : "m"
}

num2index = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def main(i):
    psm = ips.from_log('1646909402.977471329s.json', i)
    if psm.tick == 0:
        reset()
    psm.config
    logger.log(f'--- tick {psm.tick} ---')
    cont = Controller()
    try:
        cont.init(psm)
        cont.run()
    except Exception as e:
        logger.log(traceback.format_exc())
        logger.flush()
        reset()
        global had_error
        if not had_error:
            had_error = True
            main(i)  # try again, why not)
        raise e
    logger.flush()
    if psm.tick == 99:
        logger.next_log()
    print(psm.orders.humanize())
    # psm.save_and_exit()


class Controller:
    def __init__(self) -> None:
        self.psm = None
        self.module: Module = None
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
        self.doubles_off: dict[(str, str), bool] = {}
        self.storage2delta: dict[str, float] = {}

    def run(self):
        self.module.proceed()
        self.module.proceed()

        b = self.module.get_storages_available()
        if b != 0:
            self.module.order_power_recursive(-self.module.get_delta() / b)

        b = self.module.get_storages_available()
        if b != 0:
            self.module.order_power_recursive(-self.module.get_delta() / b)

        b = self.module.get_storages_available()
        if b != 0:
            self.module.order_power_recursive(-self.module.get_delta() / b)

        b = self.module.get_storages_available()
        if b != 0:
            self.module.order_power_recursive(-self.module.get_delta() / b)
        
        self.exchange()
        self.order()
        delta = self.module.get_delta()

        print(delta)

    def init(self, psm: Powerstand):
        self.psm = psm
        location2addr = {}
        for obj in psm.objects:
            if obj.type in stations:
                location2addr[obj.path[0]] = obj.address[0]

        for i, net in psm.networks.items():
            if len(net.location) == 0:
                continue
            ind = type2letter[net.location[-1].id[0]] + num2index[net.location[-1].id[1]]
            if ind not in self.addr2nets:
                self.addr2nets[ind] = {}
            self.addr2nets[ind][net.location[-1].line] = i
            # self.addr2nets[location2addr[net.location[:-1]]][net.location[-1].line] = i

        for obj in psm.objects:
            if len(obj.address) > 1:
                self.doubles_off[obj.address] = False
            if obj.type == 'storage':
                self.storage2delta[obj.address[0]] = 0
            for i in range(len(obj.address)):
                self.addr2obj[obj.address[i]] = obj
                self.type2addrs[obj.type] += [obj.address[i]]
                if len(obj.path[i]) != 0:
                    ind = self.addr2nets[type2letter[obj.path[i][-1].id[0]] + num2index[obj.path[i][-1].id[1]]][obj.path[i][-1].line]
                    if ind not in self.net2addrs:
                        self.net2addrs[ind] = []
                    self.net2addrs[ind] += [obj.address[i]]
        
        global sunny_lines_raw
        global subsunny_lines_raw
        for l in sunny_lines_raw:
            sunny_lines_raw += [self.addr2nets[l[0]][l[1]]]
        for l in subsunny_lines_raw:
            subsunny_lines_raw += [self.addr2nets[l[0]][l[1]]]

        self.module = Module(self.type2addrs['main'][0], self)
        self.module.do_tree(self.addr2obj, self.net2addrs, self.addr2nets)
        self.module.add_delta += self.get_exchange_delta()

    def exchange(self):
        power = self.module.get_stored_raw()
        cells = self.module.get_storages_raw()
        fullness = power / cells / 100

        if fullness < 0.2:
            predict = self.module.get_approx_delta(self.psm.tick + 1)
            predict -= BUY_ADD
            if predict < 0:
                with open('SB/exchange', 'a') as exfile:
                    exfile.write(f'{self.psm.tick + 1} {-predict}\n')
                    self.psm.orders.buy(-predict, 2)
        elif fullness > 0.8:
            predict = self.module.get_approx_delta(self.psm.tick + 1)
            predict += SELL_ADD
            if predict > 0:
                with open('SB/exchange', 'a') as exfile:
                    exfile.write(f'{self.psm.tick + 1} {-predict}\n')
                    self.psm.orders.sell(predict, 3.49)

    def get_exchange_delta(self) -> float:
        if not os.path.isfile('SB/exchange'):
            return 0
        with open('SB/exchange', 'r') as exfile:
            transactions = dict(tuple((lambda x: (int(x[0]), float(x[1])))(line.split(' ')) for line in exfile.read().strip().split('\n')))
            if self.psm.tick in transactions:
                return transactions[self.psm.tick]
        return 0

    def order(self):
        for addr, val in self.storage2delta.items():
            if val < 0:
                self.psm.orders.charge(addr, -val)
            if val > 0:
                self.psm.orders.discharge(addr, val)

class Module:
    def __init__(self, addr, controller) -> None:
        self.addr = addr  # 'M9'
        self.station = None
        self.lines = [Line(controller, 0, self), Line(controller, 1, self)] if addr[0] == 'm' else \
            [Line(controller, 0, self), Line(controller, 1, self), Line(controller, 2, self)]
        self.parent = None
        self.stored = 0
        self.stored_available = 0
        self.storages = 0
        self.cont = controller
        self.add_delta = 0

    def proceed(self):
        for line in self.lines:
            for ch in line.childs:
                ch.proceed()
            line.calc_objects()
            line.inspect()

    def do_tree(self, addr2obj: dict[str, Object], net2addrs: dict[int, list[str]], addr2nets: dict[str, dict[int, int]]):
        self.station = addr2obj[self.addr]
        for line, net in addr2nets[self.addr].items():
            self.lines[line - 1].net = net
            for addr in net2addrs[net]:
                obj = addr2obj[addr]
                if obj.type in stations:
                    self.lines[line - 1].childs += [Module(addr, self.cont)]
                    self.lines[line - 1].childs[-1].do_tree(addr2obj, net2addrs, addr2nets)
                else:
                    self.lines[line - 1].objects += [obj]
            self.lines[line - 1].power_on()

    def get_delta(self) -> float:
        return sum(line.get_delta() for line in self.lines) + self.add_delta

    def get_approx_delta(self, tick) -> float:
        return sum(line.get_approx_delta(tick) for line in self.lines)

    def get_stored(self) -> float:
        return sum(line.get_stored() for line in self.lines)

    def get_stored_raw(self) -> float:
        return sum(line.get_stored_raw() for line in self.lines)

    def get_storages(self) -> int:
        return sum(line.get_storages() for line in self.lines)

    def get_storages_raw(self) -> int:
        return sum(line.get_storages_raw() for line in self.lines)

    def get_storages_available(self) -> int:
        return sum(line.get_storages_available() for line in self.lines)
    
    def get_doubles(self) -> list[(str, str)]:
        return sum(line.get_doubles() for line in self.lines)

    # заказывет по amount на каждом активном накопителе
    def order_power_recursive(self, amount):
        for line in self.lines:
            line.order_power_recursive(amount)


class Line:
    def __init__(self, controller: Controller, num: int, parent: Module) -> None:
        self.childs: list[Module] = []  # [Module]
        self.objects: list[Object] = []
        self.delta = 0
        self.parent: Module = parent
        self.powered = False
        self.cont = controller
        self.num = num
        self.net = -1

    def get_delta(self) -> float:
        x = self.delta + sum(child.get_delta() for child in self.childs)
        return self.powered * (x - abs(x) * min(x * x / 3600, .25))

    def get_approx_delta(self, tick) -> float:
        x = 0
        x -= sum(map(lambda x: get_consumption(x, tick, self.cont), self.objects))
        x += sum(map(lambda x: get_generation(x, tick, self.cont), self.objects))
        x += sum(child.get_approx_delta(tick) for child in self.childs)
        return x - abs(x) * min(x * x / 3600, .25)

    def get_stored(self) -> float:
        return self.powered * (sum(map(lambda x: get_stored(x, self.cont), self.objects)) + sum(child.get_stored() for child in self.childs))

    def get_stored_raw(self) -> float:
        return (sum(map(lambda x: get_stored(x, self.cont), self.objects)) + sum(child.get_stored() for child in self.childs))

    def get_storages(self) -> int:
        return self.powered * (sum(map(get_storages, self.objects)) + sum(child.get_storages() for child in self.childs))

    def get_storages_raw(self) -> int:
        return (sum(map(get_storages, self.objects)) + sum(child.get_storages_raw() for child in self.childs))

    def get_storages_available(self) -> int:
        return self.powered * (sum(map(get_storages_available, self.objects)) + sum(child.get_storages() for child in self.childs))

    def calc_objects(self):
        self.delta = 0
        self.delta -= sum(map(lambda x: get_consumption(x, self.cont.psm.tick, self.cont), self.objects))
        self.delta += sum(map(lambda x: get_generation(x, self.cont.psm.tick, self.cont), self.objects))
        self.delta += sum(map(lambda x: get_storage_delta(x, self.cont), self.objects))
    
    def inspect(self):
        if self.cont.psm.networks[self.net].broken > 0:
            self.power_off()
            return
        wear = self.cont.psm.networks[self.net].wear
        if wear < 0.4:
            return
        doubles = set(self.get_doubles())
        for db in doubles:
            if self.cont.doubles_off[db]:
                return
        
        step = 0.70

        if self.net in sunny_lines or self.net in subsunny_lines:
            if self.cont.psm.forecasts.sun[self.cont.psm.tick] > sun_level:
                pass
            elif self.cont.psm.tick + presun_repair_shift < 100 and self.cont.psm.forecasts.sun[self.cont.psm.tick + presun_repair_shift] > sun_level:
                step = 0.2 if self.net in sunny_lines else 0.5
        
        if wear > step:
            self.power_off()
        
    def get_doubles(self) -> list[tuple[str, str]]:
        return sum((ch.get_doubles() for ch in self.childs), []) + sum(([obj.address] for obj in self.objects if len(obj.address) > 1), [])

    def power_on(self):
        self.powered = True
        self.cont.psm.orders.line_on(self.parent.addr, self.num + 1)

    def power_off(self):
        self.powered = False
        self.cont.psm.orders.line_off(self.parent.addr, self.num + 1)
        doubles = set(self.get_doubles())
        for db in doubles:
            self.cont.doubles_off[db] = True

    # заказывет по amount на каждом активном накопителе
    def order_power_recursive(self, amount):
        for obj in self.objects:
            if obj.type != 'storage':
                continue

            self.cont.storage2delta[obj.address[0]] += amount
            self.cont.storage2delta[obj.address[0]] = max(self.cont.storage2delta[obj.address[0]], max(-15, -100 + obj.charge.now))
            self.cont.storage2delta[obj.address[0]] = min(self.cont.storage2delta[obj.address[0]], min(15, obj.charge.now))
        self.calc_objects()
        for ch in self.childs:
            ch.order_power_recursive(amount)
        

# TODO
def get_consumption(obj: Object, tick: int, cont: Controller) -> float:
    if obj.type not in consumers:
        return 0
    return -1


# TODO
def get_generation(obj: Object, tick: int, cont: Controller) -> float:
    if obj.type not in generators:
        return 0
    return 1


def get_storage_delta(obj: Object, cont: Controller) -> float:
    if obj.type != 'storage':
        return 0
    return cont.storage2delta[obj.address[0]]


def get_stored(obj: Object, cont: Controller) -> float:
    if obj.type != 'storage':
        return 0    
    return obj.charge.now - cont.storage2delta[obj.address[0]]


def get_storages(obj: Object) -> float:
    if obj.type != 'storage':
        return 0
    return 1


def get_storages_available(obj: Object) -> float:
    if obj.type != 'storage' or get_stored(obj) >= 99.9:
        return 0
    return 1



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
    for i in range(100):
        main(i)
