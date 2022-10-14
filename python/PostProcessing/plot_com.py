import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def parse_args(): -> dict
    argp = argparse.ArgumentParser()
    argp.add_argument

def plot_com(data):
    plt.figure()
    plt.plot(data.time, data.x, label='x')
    plt.plot(data.time, data.y, label='y')
    plt.plot(data.time, abs_pos, label='abs')
    plt.axhline(y=0.545, label='const. amplitude')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    args = parse_args()
    plot_com(config=args)
