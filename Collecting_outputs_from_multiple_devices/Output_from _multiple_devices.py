#!/usr/bin/env python3

from itertools import repeat
from concurrent.futures import ThreadPoolExecutor
import netmiko
import csv
import yaml
import logging
from datetime import datetime
import time

class OutputFromMultipleDevices():

    logging.basicConfig(format = '%(threadName)s %(name)s %(levelname)s: %(message)s',level=logging.INFO)

    def login_and_collect_outputs(self, devicedata, commandset):

        start_msg = '===> {} {}: {}'
        received_msg = '<=== {} {}: {}'

        x = devicedata.copy()
        x['banner_timeout'] = 10

        try:
            logging.info(start_msg.format(datetime.now(), 'Connection requested to', devicedata['ip']))
            device = netmiko.ConnectHandler(**x)
            device.enable()
        except:
            logging.info(received_msg.format(datetime.now(), 'Connection failed to', devicedata['ip']))

            return devicedata['ip'], 'Unable to login\n', False, False

        else:
            collectedoutputs = True

            logging.info(received_msg.format(datetime.now(), 'Connection established with', devicedata['ip']))
            logging.info(start_msg.format(datetime.now(), 'Collecting output from', devicedata['ip']))

            output = ''
            for command in commandset:
                try:
                    output += f"{device.send_command(command)}\n"
                except:
                    output += f"{command}\nFalse\n"
                    collectedoutputs = False

            device.disconnect()

            logging.info(received_msg.format(datetime.now(), 'Collected outputs from', devicedata['ip']))

            return devicedata['ip'], output, True, collectedoutputs


    def main(self):
        logindatalist = []
        commandsetlist = []

        print("=="*20)
        input("Please make sure that login data is stored in 'logindata.csv' file and show command is stored in 'commandset.yaml' file, hit RETURN to continue")

        print("=="*20)
        print('Reading logindata.')
        with open('input/logindata.csv') as f:
            logindatalist = list(csv.DictReader(f))

        print("=="*20)
        print('Reading show command.')
        with open('input/commandset.yaml') as f:
            commandsetlist = yaml.safe_load(f)

        print("=="*20)
        print('Connecting to devices and collecting outputs.')
        print("=="*20)
        with ThreadPoolExecutor(max_workers=5) as executor:
            result = list(executor.map(self.login_and_collect_outputs, logindatalist, repeat(commandsetlist)))

        data = list(zip(logindatalist, result))
        writedata = []

        for i in data:
            datadict = {}
            datadict = i[0].copy()
            datadict['login'] = i[1][2]
            datadict['output'] = i[1][3]
            datadict['filename'] = f'{i[0]["ip"]}_output'
            writedata.append(datadict)

        with open('output/result.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames = list(writedata[0].keys()), quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
            writer.writeheader()
            for d in writedata:
            	writer.writerow(d)

        print("=="*20)
        print('Writing Data to "output.txt" file.')
        for i in result:
            with open(f'output/outputfiles/{i[0]}_output', 'w') as f:
                f.write(i[1])
        print("=="*20)

        print("=="*20)
        input('Data written to output.txt file, hit RETURN to exit ')
        print("=="*20)



if __name__ == "__main__":
    test = OutputFromMultipleDevices()
    test.main()
