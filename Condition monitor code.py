import Adafruit_BBIO.GPIO as GPIO
import paho.mqtt.client as mqtt
import subprocess
import datetime
import time
import csv
from datetime import date
from os.path import exists
import os

file_name = "/var/lib/cloud9/Project/Log.csv"
LOG_EXIST = exists("/var/lib/cloud9/Project/Log.csv")
last_known = exists("Output log.csv")
output_log = "Output log.csv"

State = 0
retry_time = 3

client = mqtt.Client("MZK-008")
topic = "BGB"
broker_port = 1883
mqtt_broker = "192.168.0.5"  # BGB broker address
asset = "MZK-008"
out = ""

GPIO.setup("P9_15", GPIO.IN)  # optocoupler 1 input
GPIO.setup("P9_12", GPIO.OUT)  # connected LED indicator
GPIO.setup("P9_23", GPIO.IN)  # optocoupler 2 input
GPIO.setup("P9_25", GPIO.OUT)  # active LED indicator


def reboot():  # reboot function if code crashes

    print("An error as occured...")
    print("Commencing restart...")
    time.sleep(retry_time)
    print("Saving output....")
    output_log = 'Output log.csv'

    with open(output_log, 'a+') as olog:
        csvwriterO = csv.writer(olog)
        save = "%s / %s " % (out, State)
        csvwriterO.writerow([save])
    subprocess.call(["python3", "Untitled1.py"])


def error_handle():  # error handling function
    print("Error:", e)
    time.sleep(retry_time)
    print("logging error....")
    error_log = 'Error Log.csv'
    with open(error_log, 'a+') as elog:
        csvwriterE = csv.writer(elog)
        error_save = current_time, "Error :", e
        csvwriterE.writerow(error_save)


def check_network_connection():  # network check function
    try:
        subprocess.check_output(["ping", "-c", "1", mqtt_broker])
        return True
    except subprocess.CalledProcessError:
        return False


def check_broken_pipes():  # broken pipes check function
    try:
        mqtt.Client().connect(mqtt_broker)
        return False
    except ConnectionRefusedError:
        return True


def shut_down():  # shutdown code in event of power failure
    sudo_password = 'temppwd'
    command = 'shutdown -h now'.split()
    p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    sudo_prompt = p.communicate(sudo_password + '\n')[1]


def strip_char(s, chars):  # function to strip characters from recall data
    return s.translate(str.maketrans("", "", chars))


boot_up = False

while boot_up == False:

    dt_object = datetime.datetime.now()  # time object reference
    current_time = dt_object.strftime("%H:%M:%S")
    date_now = str(date.today())
    date_now_out = (date_now)

    out = ("%s,%s,%s,%s" % (date_now_out, current_time, asset, "CONNECTED"))  # initial start up sequence

    try:

        if check_network_connection() and not check_broken_pipes():

            print("Connecting to Broker")
            client.connect(mqtt_broker)
            print("connected to : ", mqtt_broker)
            GPIO.output("P9_12", GPIO.HIGH)

            client.publish(topic, out, 1)
            print(out)

            if LOG_EXIST == False:
                fields = ['Date', 'Time', 'Machine', 'State']

                with open(file_name, 'a+') as LOG:
                    csvwriter = csv.writer(LOG)
                    csvwriter.writerow(fields)
                    print("NEW FILE CREATED")

                    row_str_2 = ("NO DATA")
                    client.connect(mqtt_broker)
                    client.publish(topic, row_str_2, 1)
                    boot_up = True

            break;

    except:
        break;

while True:

    dt_object = datetime.datetime.now()  # time object reference
    current_time = dt_object.strftime("%H:%M:%S")
    date_now = str(date.today())
    date_now_out = (date_now)
    s = int(dt_object.second)

    if GPIO.input("P9_15") != True and GPIO.input("P9_23") != True and State == 0:  # cycle start logic

        out = ("%s,%s,%s,%s" % (date_now_out, current_time, asset, "CYCLE START"))
        State = 1
        with open(file_name, 'a+') as log_data:
            log = ("%s \n" % out)
            log_data.write(log)
        try:

            if check_network_connection() and not check_broken_pipes():
                client.connect(mqtt_broker)
                GPIO.output("P9_25", GPIO.HIGH)
                client.publish(topic, out, 1)
                print(out)
                continue;

        except Exception as e:

            error_handle()

        else:
            reboot()


    elif GPIO.input("P9_15") and State == 1:  # cycle end logic

        out = ("%s,%s,%s,%s" % (date_now_out, current_time, asset, "CYCLE END"))
        State = 0
        with open(file_name, 'a+') as log_data:
            log = ("%s \n" % out)
            log_data.write(log)

        try:
            if check_network_connection() and not check_broken_pipes():
                client.connect(mqtt_broker)
                GPIO.output("P9_25", GPIO.LOW)
                client.publish(topic, out, 1)
                print(out)
                continue;

        except Exception as e:

            error_handle()

        else:
            reboot()

    GPIO.cleanup()

