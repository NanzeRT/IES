import ips
from shutil import rmtree as rmdir
import os
import traceback
import numpy as np

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

type2letter = {
    "main": "M",
    "mainA": "e",
    "mainB": "m"
}


def main():
    psm = ips.init_test()
    if psm.tick == 0:
        reset()
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
            main()  # try again, why not)
        raise e
    logger.flush()
    if psm.tick == 99:
        logger.next_log()
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

    def run(self):
        self.module.proceed()
        print(self.module.get_delta())

    def init(self, psm: Powerstand):
        self.psm = psm
        location2addr = {}
        for obj in psm.objects:
            if obj.type in stations:
                location2addr[obj.path[0]] = obj.address[0]

        for i, net in psm.networks.items():
            if len(net.location) == 0:
                continue
            if location2addr[net.location[:-1]] not in self.addr2nets:
                self.addr2nets[location2addr[net.location[:-1]]] = {}
            self.addr2nets[location2addr[net.location[:-1]]][net.location[-1].line] = i

        for obj in psm.objects:
            if len(obj.address) > 1:
                self.doubles_off[obj.address] = False
            for i in range(len(obj.address)):
                self.addr2obj[obj.address[i]] = obj
                self.type2addrs[obj.type] += [obj.address[i]]
                if len(obj.path[i]) != 0:
                    ind = self.addr2nets[location2addr[obj.path[i][:-1]]][obj.path[i][-1].line]
                    if ind not in self.net2addrs:
                        self.net2addrs[ind] = []
                    self.net2addrs[ind] += [obj.address[i]]

        self.module = Module(self.type2addrs['main'][0])
        self.module.do_tree(self.addr2obj, self.net2addrs, self.addr2nets)


class Module:
    def __init__(self, addr, controller) -> None:
        self.addr = addr  # 'M9'
        self.station = None
        self.lines = [Line(controller, 0), Line(controller, 1)] if addr[0] == 'm' else \
            [Line(controller, 0), Line(controller, 1), Line(controller, 2)]
        self.parent = None
        self.stored = 0
        self.stored_available = 0
        self.storages = 0
        self.cont = controller

    def proceed(self):
        for line in self.lines:
            for ch in line.childs:
                ch.proceed()
            line.calc_objects()
            self.inspect()

    def do_tree(self, addr2obj: dict[str, Object], net2addrs: dict[int, list[str]],
                addr2nets: dict[str, dict[int, int]]):
        self.station = addr2obj[self.addr]
        for line, net in addr2nets[self.addr].items():
            for addr in net2addrs[net]:
                obj = addr2obj[addr]
                if obj.type in stations:
                    self.lines[line - 1].childs += [Module(addr, self.cont)]
                    self.lines[line - 1].childs[-1].do_tree(addr2obj, net2addrs, addr2nets)
                else:
                    self.lines[line - 1].objects += [obj]

    def get_delta(self) -> float:
        return sum(line.get_delta() for line in self.lines)

    def get_stored(self) -> float:
        return sum(line.get_stored() for line in self.lines)

    def get_storages(self) -> int:
        return sum(line.get_storages() for line in self.lines)

    def get_doubles(self) -> list[(str, str)]:
        return sum(line.get_doubles() for line in self.lines)


class Line:
    def __init__(self, controller: Controller, num) -> None:
        self.childs: list[Module] = []  # [Module]
        self.objects: list[Object] = []
        self.delta = 0
        self.parent: Module = None
        self.powered = False
        self.cont = controller
        self.num = num

    def get_delta(self) -> float:
        x = self.delta + sum(child.get_delta() for child in self.childs)
        return x - abs(x) * min(x * x / 3600, .25)

    def get_stored(self) -> float:
        return sum(map(get_stored, self.objects)) + sum(child.get_stored() for child in self.childs)

    def get_storages(self) -> int:
        return sum(map(get_storages, self.objects)) + sum(child.get_storages() for child in self.childs)

    def calc_objects(self):
        self.delta = 0
        self.delta -= sum(map(get_consumption, self.objects))
        self.delta += sum(map(get_generation, self.objects))
        self.delta += sum(map(get_storage_delta, self.objects))

    def inspect(self):
        wear = self.cont.psm.networks[self.cont.addr2nets[self.parent.addr][self.num]].wear
        if wear < 0.4:
            return
        doubles = set(self.get_doubles())
        for db in doubles:
            if self.cont.doubles_off[db]:
                return

    def get_doubles(self) -> list[tuple[str, str]]:
        return sum(ch for ch in self.childs) + sum(obj.address for obj in self.objects if len(obj.address) > 1)


base_sun_coors={s2:[[9.118882164855824, 5.2001953125], [6.175676335499869, 2.255859375]], s3:[[9.118882164855824, 5.625], [6.175676335499869, 2.51953125]], s4:[[9.118882164855824, 5.6396484375], [6.175676335499869, 2.6220703125]], s5:[[9.118882164855824, 5.0390625], [6.175676335499869, 2.3291015625]], s6:[[9.118882164855824, 5.9619140625], [6.175676335499869, 3.0029296875]], s7:[[9.118882164855824, 6.240234375], [6.175676335499869, 3.1787109375]], s8:[[9.118882164855824, 5.9033203125], [6.175676335499869, 2.9736328125]], s9:[[9.118882164855824, 4.6728515625], [6.175676335499869, 2.138671875]], sB:[[9.118882164855824, 5.830078125], [6.175676335499869, 2.9443359375]], sC:[[9.118882164855824, 6.1669921875], [6.175676335499869, 3.2080078125]], sD:[[9.118882164855824, 5.9765625], [6.175676335499869, 3.017578125]], sE:[[9.118882164855824, 5.1123046875], [6.175676335499869, 2.431640625]], sF:[[9.118882164855824, 5.1416015625], [6.175676335499869, 2.5634765625]], sG:[[9.118882164855824, 6.2109375], [6.175676335499869, 3.251953125]], sH:[[9.118882164855824, 6.6796875], [6.175676335499869, 3.5595703125]], sI:[[9.118882164855824, 6.15234375], [6.175676335499869, 3.1640625]], sJ:[[9.118882164855824, 4.658203125], [6.175676335499869, 2.0654296875]], sK:[[9.118882164855824, 6.4599609375], [6.175676335499869, 3.4423828125]], sM:[[9.118882164855824, 6.767578125], [6.175676335499869, 3.603515625]], sN:[[9.118882164855824, 6.298828125], [6.175676335499869, 3.2666015625]]}
def open_file(cont:Controller) ->None:
    our_suns = cont.type2addrs['solar']
    our_suns_coors=[base_sun_coors[i] for i in our_suns]
    with open('SB/exchange', 'w') as s:
        s.write(our_suns_coors)
def read_file(cont:Controller):
    with open('SB/exchange', 'r') as s:
        data=eval(s.read())
    return data

def open_again(cont:Controller,array) -> None:
    with open('SB/exchange', 'w') as s:
        s.write(array)

def tick_sun_formule_update(cont:Controller,tick:int) -> None:
    sun_fls == [[] for _ in range(len(cont.type2addrs['solar']))]
    if tick==0:
        open_file()
    else:
        our_sun_coors=read_file()
        our_suns = cont.type2addrs['solar']
        for i in range(len(our_sun_coors)):
            our_sun_coors[i].append([cont.psm.sun.now,our_suns[i].power.now.generated])
            arr=np.array(our_sun_coors[i])
            sun_fls[i]=sun_formule(arr)
        open_again(our_sun_coors)

def sun_formule(points):

   x = points[:, 0]
   y = points[:, 1]

   X = np.vstack((np.ones(x.shape[0]), x)).T
   normal_matrix = np.dot(X.T, X)
   moment_matrix = np.dot(X.T, y)

   beta_hat = np.dot(np.linalg.inv(normal_matrix), moment_matrix)
   b = beta_hat[0]
   koef = beta_hat[1]
   y_hat = b + koef * x

   points_hat = np.vstack((x, y_hat)).T

   return koef,b

forecast=[ [] ]
#pop(0) - названия
def tick_split_forecasts(tick):
    return forecast[tick]

def group_forecasts(tick:int):
    tick_forecast = tick_split_forecasts[tick]
    grouped=defaultdict(list)
    grouped['solar']=tick_forecast[:8]
    grouped['wind']=tick_forecast[8:16]
    grouped['hospital']=tick_forecast[16:24]
    grouped['houseA']=tick_forecast[24:32]
    grouped['houseB']=tick_forecast[32:40]
    return grouped

def type_forecast(tick,type):
    group=group_forecasts(tick)[type]
    if type in ('solar','wind'):
        return min(group)
    return max(group)

def get_generation(obj: Object, tick: int, cont:Controller) -> float:
    type=obj.type
    addr=obj.address
    last_gen=obj.power.now.generated
    if type=='solar':
        our_suns=cont.type2addrs['solar']
        ind=our_suns.index(addr)
        k,b=sun_fls[ind]
        power=k * type_forecast(tick+1,type) + b
        return power
    elif type=='wind':
        pass
    else:
        pass

def get_consumption(obj:Object, tick: int, cont:Controller) -> float:
    type=obj.type
    last_forecast = type_forecast(tick, type)
    last_consumption=obj.power.now.consumed
    if last_forecast:
        koef = last_consumption / last_forecast
        predict_cons = koef * type_forecast(tick + 1, type)
        return predict_cons
    else:
        return 0

def get_storage_delta(obj: Object) -> float:
    if obj.type != 'storage':
        return 0
    return 0.1


def get_stored(obj: Object) -> float:
    if obj.type != 'storage':
        return 0
    return obj.charge.now


def get_storages(obj: Object) -> float:
    if obj.type != 'storage':
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
    main()

