import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

def createParser():
    parser = argparse.ArgumentParser(description='Coordinate transform from degree Lat Lon to meters N E using WGS84.')
    parser.add_argument('--lat',
                        help='latitude WGS84 input *.dat file',
                        default='tmp/LatWGS84.dat',
                        required=False, type=argparse.FileType('rb'))
    parser.add_argument('--lon',
                        help='longitude WGS84 input *.dat file',
                        default='tmp/LonWGS84.dat',
                        required=False, type=argparse.FileType('rb'))
    parser.add_argument('--n',
                        help='output *.dat file for N coordinate in meters',
                        default='tmp/N.dat',
                        required=False)
    parser.add_argument('--e',
                        help='output *.dat file for E coordinate in meters',
                        default='tmp/E.dat',
                        required=False)
    parser.add_argument('--plot',
                        help='show plot flag',
                        action='store_true',
                        required=False)
    parser.add_argument('--scale',
                        help='Коэффициент, масштаба входных данных',
                        default=1.0,
                        type=float,
                        required=False)
    return parser

class Figure:
    def __init__(self):
        self.files = []

    def plot(self):
        with open(self.files[0], "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()
            # print(data)


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    
    lat = list()
    lat = np.array([np.fromfile(namespace.lat.name, dtype='d')[0:None:2],
                    np.fromfile(namespace.lat.name, dtype='d')[1:None:2]])

    lon = list()
    lon = np.array([np.fromfile(namespace.lon.name, dtype='d')[0:None:2],
                    np.fromfile(namespace.lon.name, dtype='d')[1:None:2]])

                    
    lat[1] = lat[1]/namespace.scale;
    lon[1] = lon[1]/namespace.scale;
    
    # Параметры элипсойда
    ellips_a = 6378137.0;
    ellips_e2 = 0.00669437999014133;
    ellips_c1 = ellips_a * (1 - ellips_e2);

    lat0 = lat[1][-1]
    lon0 = lon[1][-1]
    sin_lat = np.sin(np.deg2rad(lat[1]));
    c2 = (1.0 - ellips_e2 * (sin_lat * sin_lat));

    if (lat0 > -85) and (lat0 < 85):
        cos_lat = np.cos(np.deg2rad(lat[1]));
    else:
        cos_lat = np.cos(np.deg2rad(85));

    met2grad = np.rad2deg((np.sqrt(c2 * c2 * c2) / ellips_c1) / cos_lat);
    grd2met = 1.0 / met2grad;

    N = 111131.777414176 * (lat[1] - lat0)

    E = grd2met*(lon[1] - lon0)

    outarr = np.zeros(len(lat[0])*2, dtype='d')
    outarr[0::2] = lat[0]

    outarr[1::2] = N
    f = open(namespace.n, 'wb')
    outarr.tofile(f)
    f.close()

    outarr[1::2] = E
    f = open(namespace.e, 'wb')
    outarr.tofile(f)
    f.close()

    if namespace.plot:
        plt.plot(E[100:], N[100:])
        plt.xlabel('E (m)')
        plt.ylabel('N (m)')
        plt.grid(True)
        #plt.savefig("test.png")
        plt.show()

    #print(lat)







