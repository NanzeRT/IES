import ips


class Controller:
    def __init__(self) -> None:
        pass

    def run(self, psm):
        pass


if __name__ == '__main__':
    psm = ips.init()
    cont = Controller()
    cont.run(psm)
    psm.save_and_exit()
