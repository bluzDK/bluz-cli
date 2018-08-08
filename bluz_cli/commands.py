import argparse
import subprocess
import requests
import os
import bluz_cli
import serial
import json

from api_url import api_url

class Commands:
    """
    Defines the bluz CLI commands
    """

    @staticmethod
    def provision(args):
        """
        Provisions an nrf51822 board to run on the Particle cloud
        
        :return: True or False
        """

        # parse out the args
        parser = argparse.ArgumentParser(description='Programs and provisions bluz-based boards for the Particle cloud')
        parser.add_argument('-p', '--programmer', default='jlink', help='programmer, either stlink or jlink')
        parser.add_argument('-s', '--port', default='', help='serial port for bluz')
        parser.add_argument('-a', '--api_key', default='', help='API Key for provisioning, contact sales at hello@bluz.io for a key')
        parser.add_argument('-i', '--product_id', default='103', help='Product ID to provision, 103 for bluz DK and 269 for bluz Gateway')

        opts = parser.parse_args(args)

        programmer = opts.programmer
        serial_port = opts.port
        api_key = opts.api_key
        product_id = opts.product_id

        if api_key == '':
            raise Exception("Must provide an API Key")

        try:
            args = ['--info']
            out = Commands.__run_adalink_command(programmer, args)
        except subprocess.CalledProcessError:
            raise Exception("Unable to communiate with board, is it properly connected?")
        except OSError:
            raise Exception("Adalink must be installed. Please refer to documentation.")

        print "---------------------------------------"
        print "Getting Hardware ID"
        print "---------------------------------------"
        print out
        print ""

        for line in out.split('\n'):
            if ':' in line:
                if line.split(':')[0].strip() == 'Device ID':
                    hw_id = str(line.split(':')[1].strip())

        nrf_id = ""
        i = len(hw_id)
        for val in range(len(hw_id) / 2):
            nrf_id += hw_id[i - 2:i]
            i -= 2

        try:
            os.remove('device.bin')
            os.remove('device.pem')
            os.remove('device.pub.pem')
        except:
            pass

        print "---------------------------------------"
        print "Generating Keys"
        print "---------------------------------------"
        print args
        args = ["particle"]
        args.append('keys')
        args.append('new')
        args.append('--protocol')
        args.append('tcp')
        subprocess.check_output(args)
        os.rename('./device.der', './device.bin')

        print "---------------------------------------"
        print "Provisioning Device"
        print "---------------------------------------"
        with open('device.pub.pem', 'rb') as f:
            public_key = f.read()

        # send nrf_id to API to get full device ID
        data = {
            "nrf_id": nrf_id,
            "product_id": product_id,
            "public_key": public_key
        }
        headers = {
            'x-api-key': api_key
        }
        r = requests.post(api_url + '/provision', data=data, headers=headers)
        response = json.loads(r.text)
        if r.status_code == 403:
            os.remove('device.bin')
            os.remove('device.pem')
            os.remove('device.pub.pem')
            raise Exception("Permission denied, please contact sales at hello@bluz.io for a key")
        elif r.status_code != 200:
            os.remove('device.bin')
            os.remove('device.pem')
            os.remove('device.pub.pem')
            raise Exception(
                "Unknown server error: " + response + "\n. If the issue persists, please contact support at hello@bluz.io")

        device_id = response['device_id']

        print "Device ID: " + device_id

        print "---------------------------------------"
        print "Wiping Hardware Flash"
        print "---------------------------------------"
        args = ['--wipe']
        out = Commands.__run_adalink_command(programmer, args)
        print out
        print ""

        print "---------------------------------------"
        print "Programming Provisioning Firmware"
        print "---------------------------------------"
        f = open('./int.bin', 'w')
        counter = device_id[4:8]
        first = int('0x' + counter[2:], 16)
        second = int('0x' + counter[:2], 16)
        idArray = bytearray([first, second])
        f.write(idArray)
        f.close()

        full_path = os.path.join(bluz_cli.__path__[0], 'resources')
        firmware_path = os.path.join(full_path, 'bluz_dk_firmware' if product_id == '103' else 'gateway_firmware')

        args = ['--program-bin']
        args.append('./int.bin')
        args.append('0x3F000')
        args.append('--program-bin')
        args.append('./device.bin')
        args.append('0x3F400')
        args.append('--program-bin')
        args.append(os.path.join(full_path, 'keys/cloud.public.bin'))
        args.append('0x3F800')

        args.append('--program-hex')
        args.append(os.path.join(full_path, 's110/s110_softdevice.hex'))
        args.append('--program-hex')
        args.append(os.path.join(firmware_path, 'provisioning_firmware/bootloader.hex'))

        args.append('--program-hex')
        args.append(os.path.join(firmware_path, 'provisioning_firmware/system-part1.hex'))

        out = Commands.__run_adalink_command(programmer, args)
        print out
        print ""

        if serial_port != '':
            s = serial.Serial(port=serial_port, baudrate=38400)
            s.readline()
            s.close()

            print "---------------------------------------"
            print "Programming Production Firmware"
            print "---------------------------------------"

            args = ['--program-hex']
            if product_id == '103':
                args.append(os.path.join(full_path, 's110/s110_softdevice.hex'))
            else:
                args.append(os.path.join(full_path, 's120/s120_softdevice.hex'))

            args.append('--program-hex')
            args.append(os.path.join(firmware_path, 'production_firmware/bootloader.hex'))

            args.append('--program-hex')
            args.append(os.path.join(firmware_path, 'production_firmware/system-part1.hex'))
            args.append('--program-hex')
            args.append(os.path.join(firmware_path, 'production_firmware/tinker.hex'))

            out = Commands.__run_adalink_command(programmer, args)
            print out

        print "---------------------------------------"
        print "Cleaning Up"
        print "---------------------------------------"
        os.remove('int.bin')
        os.remove('device.bin')
        os.remove('device.pem')
        os.remove('device.pub.pem')

    @staticmethod
    def program(args):

        parser = argparse.ArgumentParser(description='Programs and provisions bluz-based boards for the Particle cloud')
        parser.add_argument('-p', '--programmer', default='jlink', help='programmer, either stlink or jlink')
        parser.add_argument('-i', '--product_id', default='103',
                            help='Product ID to provision, 103 for bluz DK and 269 for bluz Gateway')

        opts = parser.parse_args(args)

        programmer = opts.programmer
        product_id = opts.product_id

        print "---------------------------------------"
        print "Programming Production Firmware"
        print "---------------------------------------"

        full_path = os.path.join(bluz_cli.__path__[0], 'resources')
        firmware_path = os.path.join(full_path, 'bluz_dk_firmware' if product_id == '103' else 'gateway_firmware')

        args = ['--program-hex']
        if product_id == '103':
            args.append(os.path.join(full_path, 's110/s110_softdevice.hex'))
        else:
            args.append(os.path.join(full_path, 's120/s120_softdevice.hex'))

        args.append('--program-hex')
        args.append(os.path.join(firmware_path, 'production_firmware/bootloader.hex'))

        args.append('--program-hex')
        args.append(os.path.join(firmware_path, 'production_firmware/system-part1.hex'))
        args.append('--program-hex')
        if product_id == '103':
            args.append(os.path.join(firmware_path, 'production_firmware/tinker.hex'))
        else:
            args.append(os.path.join(firmware_path, 'production_firmware/bluz_gateway.hex'))      

        out = Commands.__run_adalink_command(programmer, args)
        print out

    @staticmethod
    def __run_adalink_command(programmer, args):
        local_args = ["adalink"]
        local_args.append('nrf51822')
        local_args.append('--programmer')
        local_args.append(programmer)

        local_args += args
        output = subprocess.check_output(local_args)
        return output













