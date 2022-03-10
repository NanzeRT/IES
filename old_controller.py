import ips

psm = ips.init()
tick = psm.tick

DO_THING = False
offticks = {49, 50}

SELL = 9
SELL_ = 25
BUY = 15

CELL_DISCHARGE = 10
CELL_CHARGE = 10
MAX_BATTERY = 50
STORAGE_DISCHARGE = 15
STORAGE_CHARGE = 15
MAX_STORAGE = 100
MAX_DIESEL = 5

station_types = {"miniA", "miniB", "main"}


class ControlSystem:
    def main(self):
        # if tick < 5:
        #     self.num = 8
        # elif tick % 3 == 0:
        #     self.num = 8
        # else:
        #     self.num = 0
        self.num = 10

        psm.orders.tps("tH", self.num)
        print(f'burning {self.num}')
        self.def_objects()
        if tick == 0:
            self.tick_one()
        self.def_casts()
        self.generation = self.calc_generation()
        self.consumption = self.calc_consume() * 1.05
        self.reserve()
        self.log()

    def __init__(self):
        self.consumption = 0
        self.generation = 0
        self.stored = 0
        self.cell_stored = 0

        self.storages = set()
        self.cells = {}
        self.diesels = {}

        self.objects = {
            'wind': [],
            'solar': [],
            'TPS': []
        }
        self.obj_adr = {
            'wind': [],
            'solar': [],
            'TPS': []
        }

        self.houseA_c = None
        self.houseB_c = None
        self.hospital_c = None
        self.factory_c = None
        self.wind_c = None
        self.sun_c = None

    def def_objects(self):
        for obj in psm.objects:
            if obj.type not in self.objects:
                self.objects[obj.type] = []
                self.obj_adr[obj.type] = []
            self.objects[obj.type] += [obj]
            self.obj_adr[obj.type] += [obj.address]

            if obj.type == 'storage':
                adr = obj.address[0]
                self.storages.add(adr)
                self.stored += obj.charge.now
            elif obj.type in station_types:
                adr = obj.address[0]
                # Включение
                for i in range(2 if obj.type == "miniB" else 3):
                    if tick not in offticks or not DO_THING:
                        psm.orders.line_on(adr, i + 1)
                    else:
                        psm.orders.line_off(adr, i + 1)

                # Зачёт модулей
                for mod in obj.modules:
                    if type(mod) == ips.Diesel:
                        if adr not in self.diesels:
                            self.diesels[adr] = 0
                        self.diesels[adr] += 1
                    elif type(mod) == ips.Cell:
                        self.cell_stored += mod.charge
                        if adr not in self.cells:
                            self.cells[adr] = 0
                        self.cells[adr] += 1

    def def_casts(self):
        try:
            0/0
            forecast_log = open("forecast", 'r')
            data = forecast_log.read().split('\n')
        except:
            forecast_log = open("forecast", 'w')
            data = ''

        if len(data) < 8 or tick == 0:
            self.houseA_c = list(range(8))
            self.houseB_c = list(range(8))
            self.hospital_c = list(range(8))
            self.factory_c = list(range(8))
            self.wind_c = list(range(8))
            self.sun_c = list(range(8))
        else:
            self.houseA_c = list(map(int, data[0].split()))
            if 'houseA' in self.objects:
                self.houseA_c = filter_cast(
                    psm.forecasts.houseA, self.houseA_c, self.objects['houseA'][0].power.now.consumed)
            self.houseB_c = list(map(int, data[1].split()))
            if 'houseB' in self.objects:
                self.houseB_c = filter_cast(
                    psm.forecasts.houseB, self.houseB_c, self.objects['houseB'][0].power.now.consumed)
            self.hospital_c = list(map(int, data[2].split()))
            if 'hospital' in self.objects:
                self.hospital_c = filter_cast(
                    psm.forecasts.hospital, self.hospital_c, self.objects['hospital'][0].power.now.consumed)
            self.factory_c = list(map(int, data[3].split()))
            if 'factory' in self.objects:
                self.factory_c = filter_cast(
                    psm.forecasts.factory, self.factory_c, self.objects['factory'][0].power.now.consumed)
            self.wind_c = list(map(int, data[4].split()))
            self.wind_c = filter_cast(
                psm.forecasts.wind, self.wind_c, psm.wind.now)
            self.sun_c = list(map(int, data[5].split()))
            self.sun_c = filter_cast(
                psm.forecasts.sun, self.sun_c, psm.sun.now)

        forecast_log.close()
        forecast_log = open("forecast", 'w')
        s = '\n'.join((' '.join(map(str, _casts)) for _casts in
                      (self.houseA_c, self.houseB_c, self.hospital_c, self.factory_c, self.wind_c, self.sun_c)))
        forecast_log.write(s)
        forecast_log.close()

    def calc_generation(self):
        generation = 0
        with open('buy', 'r') as buy:
            seller = buy.read().split()
            if str(tick) in seller:
                generation += BUY
        for obj in psm.objects:
            if obj.type == "wind":
                generation += obj.power.now.generated * \
                    cast_multiplier(psm.forecasts.wind, self.wind_c) ** .1
            elif obj.type == "solar":
                generation += obj.power.now.generated * \
                    cast_multiplier(psm.forecasts.sun, self.sun_c)
            elif obj.type == "TPS":
                generation += max(0, obj.power.now.generated * 0.6 - 0.5 +
                                  self.num * (- self.num**2 / 128 + self.num / 8 + 0.4))

        return generation

    def calc_consume(self):
        consumption = 0
        with open('sell', 'r') as sell:
            seller = sell.read().split()
            if str(tick) in seller:
                consumption += SELL if psm.fails[tick] else SELL_
        for obj in psm.objects:
            if obj.type == "houseA":
                consumption += obj.power.now.consumed * \
                    cast_multiplier(psm.forecasts.houseA, self.houseA_c)
            elif obj.type == "houseB":
                consumption += obj.power.now.consumed * \
                    cast_multiplier(psm.forecasts.houseB, self.houseB_c)
            elif obj.type == "factory":
                consumption += obj.power.now.consumed * \
                    cast_multiplier(psm.forecasts.factory, self.factory_c)
            elif obj.type == "hospital":
                consumption += obj.power.now.consumed * \
                    cast_multiplier(psm.forecasts.hospital, self.hospital_c)
        with open('cons', 'r') as f:
            f = f.read()
            last_cons = (float(f) if len(f) > 0 else consumption)
        with open('cons', 'w') as f:
            f.write(str(consumption))
        with open('gen', 'r') as f:
            f = f.read()
            last_gen = (float(f) if len(f) > 0 else self.generation)
        with open('gen', 'w') as f:
            f.write(str(self.generation))
        consumption += \
            sum(net.losses for net in psm.networks.values()) * \
            (max(consumption, self.generation) / max(last_cons, last_gen, 1)) ** 2
        return consumption

    def get_delta(self):
        return self.generation - self.consumption

    def reserve(self):
        if (len(self.storages) + sum(self.cells.values())) == 0:
            return
        if (not DO_THING or tick + 1 not in offticks) and self.stored / (len(self.storages) + sum(self.cells.values())) / MAX_STORAGE < .1:
            with open('buy', 'a') as buy:
                buy.write(f'{tick + 1} ')
                psm.orders.buy(BUY, 2)

        if (not DO_THING or tick + 1 not in offticks) and self.stored / (len(self.storages) + sum(self.cells.values())) / MAX_STORAGE > .85 or \
           (not DO_THING or tick + 1 not in offticks) and self.stored / (len(self.storages) + sum(self.cells.values())) / MAX_STORAGE > .45 and 48 <= tick <= 70:
            with open('sell', 'a') as sell:
                sell.write(f'{tick + 1} ')
                psm.orders.sell(SELL if psm.fails[tick + 2] else SELL_, 3.49)

        if self.stored / (len(self.storages) + sum(self.cells.values())) / 9.5 >= 100 - tick:
            if self.storages:
                char = 10
                for adr in self.storages:
                    psm.orders.discharge(adr, char)
                self.generation += char * len(self.storages)
            if self.cells:
                count = 10
                char = min(-self.get_delta() / count,
                           self.cell_stored / count, STORAGE_DISCHARGE)
                for adr in self.cells.keys():
                    psm.orders.discharge(adr, char)
                self.generation += char * count
        elif self.get_delta() > 0:
            if self.storages:
                char = min(self.get_delta() / len(self.storages), MAX_STORAGE -
                           self.stored / len(self.storages), STORAGE_CHARGE)
                print(f'charging on {char}')
                for adr in self.storages:
                    psm.orders.charge(adr, char)
                self.consumption += char * len(self.storages)
            if self.cells:
                count = sum(self.cells.values())
                char = min(self.get_delta() / count, MAX_STORAGE -
                           self.cell_stored / count, STORAGE_CHARGE)
                for adr in self.cells.keys():
                    psm.orders.charge(adr, char)
                self.consumption += char * count
        else:
            if self.storages:
                char = min(-self.get_delta() / len(self.storages),
                           self.stored / len(self.storages), STORAGE_DISCHARGE)
                for adr in self.storages:
                    psm.orders.discharge(adr, char)
                self.generation += char * len(self.storages)
            if self.cells:
                count = sum(self.cells.values())
                char = min(-self.get_delta() / count,
                           self.cell_stored / count, STORAGE_DISCHARGE)
                for adr in self.cells.keys():
                    psm.orders.discharge(adr, char)
                self.generation += char * count
            if self.diesels:
                count = sum(self.diesels.values())
                char = min(-self.get_delta() / count, MAX_DIESEL)
                for adr in self.diesels.keys():
                    psm.orders.diesel(adr, char)
                self.generation += char * count

    def log(self):
        print(f'delta: {self.get_delta()}')
        print(f'objects: {self.obj_adr}')
        print(self.consumption,
              self.generation,
              self.stored,
              self.cell_stored)

        logger = open('log', 'a')
        logger.write(f'tick {psm.tick}\n')
        logger.write(f'sun: {psm.sun.now} solar powers:' +
                     f' {" ".join(f"{obj.address} - {obj.power.now.generated}" for obj in self.objects["solar"])}\n')
        logger.write(f'wind: {psm.wind.now} wind powers:' +
                     f' {" ".join(f"{obj.address} - {obj.power.now.generated}" for obj in self.objects["wind"])}\n')
        logger.write(f'tps: {psm.wind.now} tps powers:' +
                     f' {" ".join(f"{obj.address} - {obj.power.now.generated}" for obj in self.objects["TPS"])}\n')
        logger.write(f'burning {self.num}\n')
        print(f'tps: {psm.wind.now} tps powers:' +
              f' {" ".join(f"{obj.address} - {obj.power.now.generated}" for obj in self.objects["TPS"])}\n')
        logger.write(f'final delta: {self.get_delta()}\n')
        logger.write('---------------------------\n')
        logger.close()

    def tick_one(self):
        open('forecast', 'w').close()
        open('cons', 'w').close()
        open('gen', 'w').close()
        open('sell', 'w').close()
        open('buy', 'w').close()
        for obj in psm.objects:
            if obj.type == "houseA":
                self.consumption += psm.forecasts.houseA[0][tick]
            if obj.type == "houseB":
                self.consumption += psm.forecasts.houseB[0][tick]
            if obj.type == "factory":
                self.consumption += psm.forecasts.factory[0][tick]
            if obj.type == "hospital":
                self.consumption += psm.forecasts.hospital[0][tick]


def filter_cast(cast, nums: list, val):
    _nums = nums[:]
    for i in _nums:
        if abs(cast[i][tick - 1] - val) > 0.5:
            nums.remove(i)
    return nums


def cast_multiplier(cast, nums):
    if tick == 0:
        return 1
    return max(cast[i][tick] / (cast[i][tick - 1] + 0.01) for i in nums)


if __name__ == '__main__':
    ControlSystem().main()
    print(psm.orders.humanize())
    psm.save_and_exit()
