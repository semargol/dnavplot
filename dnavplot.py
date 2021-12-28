#!/usr/bin/python3
import sys
import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import matplotlib

def createParser():
    parser = argparse.ArgumentParser(description=r'Plotting data from *dat files.',
                                     epilog="Press 'h' at plot window to show menu in console.")
    parser.add_argument('-f', '--files', nargs='+',
                        help='files to plot. Example: -f out\AltWGS84.dat out\LatWGS84.lat',
                        required=True, type=argparse.FileType('rb'))
    parser.add_argument('-c', '--configure', nargs='+',
                        help='Configure of plots on figure. Example: -f out\AltWGS84.dat '
                             'new\Alt.dat out\LatWGS84.lat -c 2 1. Show 2 line Alt on first plot '
                             'and 1 line Lat on second plot.',
                        required=False, type=int)
    parser.add_argument('-u', '--update', help=' Real-time update period in second.',
                        required=False, type=float)
    #parser.add_argument('-np', '--number_of_point', help=' Number of last point to plotting. ',
    #                    required=False, type=int)
    parser.add_argument('--start_time', nargs=1,
                        help='First plotting TIME point.',
                        required=False, type=float)
    #parser.add_argument('--start_step', nargs=1,
    #                    help='First plotting STEP point.',
    #                    required=False, type=int)
    return parser

class DnavFigure:
    def __init__(self):
        self.files = []
        self.c = None  # массив - конфигурация графиков
        self.f = matplotlib.figure.Figure()
        self.a = 0  # оси
        self.l = list()  # линии графиков
        self.n = list()  # имена
        self.d = list()  # данные
        self.an = 0  # количество осей
        self.dn = 0  # количество файлов
        self.start_time = np.inf  # время начала записей
        self.span = list()  # объекты выделялки осей
        self.zoom_history = list()  # история зуммирования

    def keyPress(self,event):
        #print('press', event.key)
        sys.stdout.flush()
        if event.key == 'x':
            # zoom
            self.addSpanSelector()
        if event.key == 'z':
            self.undoZoom()
        if event.key == 'w':
            self.testZoom()
        if event.key == 't':
            self.addMarker()
        if event.key == 'q':
            exit()
        self.f.canvas.draw()

    def zoom(self, xmin, xmax):
        self.a[0].set_xlim(xmin, xmax)
        self.autoScaleY()
        self.span = list()

    def undoZoom(self):
        if len(self.zoom_history) > 1:
            #print("Select zoom = {} {}".format(self.zoom_history[-2][0], self.zoom_history[-2][1]))
            self.zoom(self.zoom_history[-2][0], self.zoom_history[-2][1])
            self.zoom_history.pop()
        else:
            x_min, x_max = [np.inf, -np.inf]
            for a in self.a:
                list_l = a.get_lines()
                for l in list_l:
                    x_data = l.get_xdata()
                    x_min = min(x_min, min(x_data))
                    x_max = max(x_max, max(x_data))
            self.a[0].set_xlim(x_min, x_max)
        self.autoScaleY()

    def autoScaleY(self):
        """" Устанавливает втоматический масштаб по оси Y для всех графиков"""
        for a in self.a:
            x_min, x_max = a.get_xlim()
            y_min, y_max = [np.inf, -np.inf]
            list_l = a.get_lines()
            for l in list_l:
                y_data = l.get_ydata()
                x_data = l.get_xdata()
                ind_min = np.transpose(np.nonzero(x_data > x_min))[0][0]
                ind_max = np.transpose(np.nonzero(x_data < x_max))[-1][0]+1
                if ind_max > ind_min:
                    y_min = min(y_min, y_data[ind_min:ind_max].min())
                    y_max = max(y_max, y_data[ind_min:ind_max].max())
                else:
                    y_min = min(y_min, min(y_data))
                    y_max = max(y_max, max(y_data))

            y_margin = (y_max - y_min) / 10
            a.set_ylim(y_min - y_margin, y_max + y_margin)

    def autoScaleX(self):
        """" Устанавливает втоматический масштаб по оси X для всех графиков"""
        for a in self.a:
            x_min, x_max = [np.inf, -np.inf]
            for l in self.l:
                x_data = l.get_xdata()

                x_min = min(x_min, min(x_data))
                x_max = max(x_max, max(x_data))

            x_margin = (x_max - x_min) / 10
            a.set_xlim(x_min - x_margin, x_max + x_margin)

    def onSelect(self, xmin, xmax):
        """" Выделение и приближение"""
        self.zoom_history.append([xmin, xmax])
        print("zoom history = {}".format(self.zoom_history))
        self.zoom(xmin, xmax)
        #for ia in range(self.an):
        #    self.span = list()

    def determinationStartTime(self):
        """" Определяет время начала записей,
        для того, чтобы вычитать это смещение.
        """
        for i in range(self.dn):
            #self.start_time = min(self.start_time, self.d[i][0][10])
            self.start_time = min(self.start_time, self.d[i][0][0])
            if len(self.d) <=1 :
                print(self.d[i])

    def addSpanSelector(self):
        """ Добавляет возможность выделять область по горизонтальной оси.
        """
        for ia in range(self.an):
            self.span.append(SpanSelector(self.a[ia], self.onSelect, 'horizontal', useblit=False,
                                              rectprops=dict(alpha=0.3, facecolor='purple')))

    def addLegend(self):
        """ Добавляет легенду.
        """
        for ax in self.a:
            ax.legend()

    def addMarker(self, marker='*'):
        """ Добавляет или убирает маркеры на линии.
        """
        for line in self.l:
            if line.get_marker() != '':
                marker = ''
            line.set_marker(marker)

    def plot(self,marker=''):
        """ Основная функция, рисующая график.
        """
        #plt.ion()
        self.dn = len(self.d)

        if self.c==None:
            self.c = np.ones(self.dn, dtype=int)

        self.an = len(self.c)

        if sum(self.c) != self.dn:
            raise NameError('Конфигурация графика не соответствует количеству входных файлов.')

        self.determinationStartTime()
        print('plot: ')
        if self.an > 1:
            self.f, self.a = plt.subplots(self.an, 1, sharex=True, squeeze=True)
        else:
            self.f, self.a = plt.subplots(self.an, 1, sharex=True, squeeze=False)
            self.a = self.a[0]

        self.f.subplots_adjust(hspace=0.1)

        i = 0
        for ia in range(self.an):
            for j in range(self.c[ia]):
                self.d[i][0] = self.d[i][0] - self.start_time # вычитаем время начала
                print("    {}".format(self.n[i]))
                line, = self.a[ia].plot(self.d[i][0], self.d[i][1], label=self.n[i], marker=marker)
                self.l.append(line)
                self.a[ia].grid(True, color='#c6c6c6', linestyle='--', linewidth=0.5)
                i += 1

        plt.xlabel('Start at ' +
                   time.strftime("%H:%M:%S",  time.gmtime(self.start_time)) +
                   '. Time in sec.')

        self.autoScaleY()
        self.addLegend()
        self.f.canvas.mpl_connect('key_press_event', self.keyPress)
        #self.onSelect(self.d[0][0][200], self.d[0][0][-1]); # Для отбрасывания начальных значений.

        plt.show()
        self.addSpanSelector()

    def update(self):
        """ Обновление графиков.
        """
        i = 0
        for ia in range(self.an):
            for j in range(self.c[ia]):
                self.d[i][0] = self.d[i][0] - self.start_time # вычитаем время начала
                self.l[i].set_xdata(self.d[i][0])
                self.l[i].set_ydata(self.d[i][1])
                i += 1
        self.f.canvas.draw()
        self.f.canvas.flush_events()
        self.autoScaleX()
        self.autoScaleY()

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    #print(namespace.start_time)

    f = DnavFigure()

    # импорт данных
    f.c = namespace.configure
    for i in namespace.files:
        f.files.append(i.name)
        f.n.append(i.name[:-4])
        f.d.append(np.array([np.fromfile(i.name, dtype='d')[0:None:2],
                             np.fromfile(i.name, dtype='d')[1:None:2]]))

    if namespace.update:
        plt.ion()
        f.plot()
        while 1:
            # Обнуляем массив данных.
            f.d = list()
            for i in namespace.files:
                f.d.append(np.array([np.fromfile(i.name, dtype='d')[0:None:2],
                                     np.fromfile(i.name, dtype='d')[1:None:2]]))
            f.update()
            f.f.canvas.flush_events()
            time.sleep(namespace.update)
    else:
        f.plot()
