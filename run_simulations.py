from subprocess import call, Popen
import re
import logging
import time
import csv
import config
from ctypes import windll, create_string_buffer                             # for windows terminal size

logging.basicConfig(
    format='|  %(asctime)s  |  [%(levelname)s]  |  %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

def main():

    metrics = dict()
    # call('PowerShell clear')
    braces()
    
    # GENERATE STARTING NETLIST FROM PROVIDED SCHEMATIC
    NETLIST0 = netlist_from_schematic(config.PROJECT_PATH + config.SCHEMATIC)

    for value in config.params:
        logging.info('Starting with ' + config.PARAMETER + ' = ' + str(value) + '\n')

        # GENERATE NEW NETLIST
        buffer_fout = config.PROJECT_PATH + config.SCHEMATIC[:-4] + "_" + config.PARAMETER + '_' + str(value) + '.net'
        new_netlist(NETLIST0, buffer_fout, value)

        # SIMULATE GENERATED NETLIST
        simulate_netlist(buffer_fout)
        logging.info('Done with ' + config.PARAMETER + ' = ' + str(value) + '.\n')

        # PARSE LOG FILE TO EXTRACT METRICS
        log_file = buffer_fout[:-3] + "log"
        print(log_file)
        metrics[value] = parse_log(log_file) # add found metrics to metrics dictionary
        logging.info('Reported efficiency is ' + str(metrics[value]))

    # WRITE RESULTS TO CSV FILE
    logging.info('Done with simulations. Writing to CSV... \n')
    generate_CSV(metrics)
    logging.info('Results ready.')
    braces()

def netlist_from_schematic(sch_file):
    # returns name of netlist file
    logging.info('Input schematic: ' + sch_file)
    logging.info('Generating starting netlist...')
    call('"' + config.LTSPICE_PATH + '" -netlist "' + sch_file + '"')
    net_file = sch_file[:-3] + 'net'
    logging.info('Done.\n')
    return net_file

def new_netlist(start_net, new_net, val):
    logging.info('Generating new netlist...')
    with open(start_net, 'r') as netlist_read:
        with open(new_net, 'w') as netlist_write:
            replaced = False
            size = len('.param ') + len(config.PARAMETER)

            for line in netlist_read:
                if (line[0:size] == '.param ' + config.PARAMETER):
                    netlist_write.write('.param ' + config.PARAMETER + ' ' + str(val) + '\n')
                    replaced = True
                else:
                    netlist_write.write(line)
            if (not replaced):
                netlist_write.write('.param ' + config.PARAMETER + ' ' + str(val) + '\n')
    logging.info('Done.')
    logging.info('Netlist file: ' + new_net)

def simulate_netlist(netlist):
    command = '"' + config.LTSPICE_PATH + '" -Run "' + netlist + '"'
    proc = Popen(command)
    logging.info('Simulation launched. Waiting ' + str(config.WAIT_TIME) + ' seconds...')
    # logging.info('Simulation netlist: ' + netlist + ' \n')
    try:
        time.sleep(config.WAIT_TIME)
    except KeyboardInterrupt:
        pass
    proc.kill()

def parse_log(log_file):
    with open(log_file, 'r') as log:
        pin = None
        pout = None

        for line in log:
            pin_match = config.pin_regex.match(line)
            pout_match = config.pout_regex.match(line)

            if pin_match:
                pin = float(pin_match.group(1))
            elif pout_match:
                pout = float(pout_match.group(1))

        # Raise an error if power values could not be extracted from log
        if (pin==None and pout==None):
            logging.error('Could not find power values from log file')
            return 0
        else:
            return [pin, pout]

def generate_CSV(met_dict):
    with open(config.RESULTS_FILE, 'w', newline='') as fout:
        fwriter = csv.writer(fout)
        fwriter.writerow(['Metric'] + [i for i in met_dict.keys()])
        fwriter.writerow(['pin'] + [i[0] for i in met_dict.values()])
        fwriter.writerow(['pout'] + [i[1] for i in met_dict.values()])
        fwriter.writerow(['eff'] + [i[1]/i[0] for i in met_dict.values()])

def braces(title = ''):
    print('\n| ' + title.center(terminal_size()-4, '-') + ' |', end='')

def terminal_size():
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
        left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
    else:
        sizex, sizey = 80, 25 # can't determine actual size - return default values

    return sizex

if __name__ == '__main__':
    main()