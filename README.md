# GAIA-Workshop

Exercises and companion material used in the [GAIA project][1]'s workshops in
schools.


## Repository structure

* `code`: Contains the code for the workshop running of the Raspberry Pi lab kit
* `demo`: Various demos used for presentations
* `firmware`: Arduino firmware for the Arduino Gauge
* `tests`: Libraries to run the workshop exercises without the lab kit


## Getting Started

### Hardware
In order to utilize the workshop as intended a [Raspberry Pi][2] with the
[Grove Pi][3] shield are required. The workshop exercises also use modified
parts from the [Electroninks Circuit Scribe][4] kit. The following list contains
most of the materials used.

* [Raspberry Pi][2]
* [Grove Pi][3]
* [Grove - LCD RGB Backlight][5]
* [Grove - Button][6] x2
* [Grove - Digital Light Sensor][7]
* [Electroninks Circuit Scribe][4]
    * Electroninks Conductive Ink
    * Two color LEDs
    * Switch
    * Two-pin connectors
        * Resistors (10k Ohms x2, 470k Ohms x2)
        * Photo-resistor
    * Two-pin Cables (Yellow - White)
    * Three-pin Cables (Yellow - Black - Red)
* [Arduino Gauge Led Rings][8]

### Software
The workshop's software is written in **Python 2.7**. It requires [Grove Pi][3]'s
software suite, which can be installed following these [instructions][9]. A few
exercises also require [python-forecastio][10] library for acquiring weather
information, which can be installed using``pip install python-forecastio``. If
you want to use the default data provider, a [SparkWorks][11] account is also
required.

The exercises are split in 4 different workshops depending on their focus

* **Workshop1**: Introductory course to familiarize the students with basic concepts
* **Workshop2**: Course to examine the lighting of the school's classrooms
* **Workshop3**: Course to examine the temperature and humidity of the classrooms
* **Workshop4**: Course to examine the power usage of the school building monitored
by the GAIA installation


## Usage

### Lab Kit
In order to run the exercises, simple navigate to the folder ``code/``. You can
execute each individual exercise simply by
```bash
python GAIA-Workshop1.1.py
```
Of course, if you want to run any other one, substitute the argument in the
command above with the filename of any other exercise.


### Testing
If you want to run the exercises in your local computer without the lab kit for
testing purposes you will have to copy the exercise from the ``code/`` directory
into the ``test/`` folder. For example from the project's root directory you can
execute
```bash
cp code/GAIA-Workshop1.1.py tests/
```
Afterwards navigate to the ``tests/`` directory and execute the exercise as
described above. If your local machine has both **Python 2** and **Python 3**,
depending which one is the default, you might need to use
```bash
python2 GAIA-Workshop1.1.py
```
to invoke **Python 2**

### properties.py
In order to use [SparkWorks][11] as your data provider, you will also need to
provide a ``properties.py`` file with your credentials and some other
configuration options. You can find a template below
```python
# -*- coding: utf-8 -*-
username = ""
password = ""
uuid = ""
GPSposition=[latitude,longitude]

# Names of the classrooms with environmental sensors.
# Choose no more than three and put them in the list
# named 'the_rooms'.
# "Room 1", "Room 2"
the_rooms = ["Room 1", "Room 2"]

# According the list above, choose the classroom which you
# want to monitor for power consumption. Despite the
# selection being done according to the classroom selected,
# the power sensor might monitor a larger part of the school,
# depending on its location. Usually choose the classroom
# the workshop is using, in order for the exercises to
# be conducted without causing disruptions to the rest of
# the school.
lab_room = "Room 1"

client_id = ""
client_secret = ""
```


## Code Structure
The workshop code follows the structure of an Arduino sketch. An exclusion is
the ``main()`` function, which is the entry point of each exercise. In there the
``setup()`` function is used to initialize the parameters of each exercise and the
``loop()`` function which handles input, output and updates the data until exit.


| Function Name         | Description   |
|-----------------------|---------------|
| ``setup()``           | Used to initialize each exercise, such as the Grove Pi I/O, the LCD screen and the Arduino Gauge led rings. Also, the connection and in some cases the initial data acquisition from the data provider happens here. Lastly, it displays a few information about the configuration, such as the username, the building and which phenomenon is being measured.|
| ``loop()``            | Updates and displays new data and handles user input from the buttons and the switch. In some cases, it handles the initial data acquisition too if it is not in ``setup()``. Input from the buttons and the switch is handled by ``checkBUtton()`` and ``checkSwitch()`` respectively.|
| ``initData()``        | Connects to the data provider. In the current implementation connects to the [SparkWorks][11] platform using the provided library. Refer to section **Using another data provider** for more information.|
| ``update[Site]Data()``| Retrieves data from the data provider. In the current implementation connects to the [SparkWorks][11] platform using the provided library. Refer to section **Using another data provider** for more information.|


## Using another data provider
If you want to use a different data provider you can redefine ``initData()``
and ``update[Site]Data()``. The only requirement is to have them return your data
in a form the rest of the exercise can utilize.

* In the case of ``initData()``, the only requirement is to return the classrooms's
or phases's names being monitored as the second product.

* In the case of ``update[Site]Data()``, the returned products are always a
timestamp in unix time and a list of 48 measurement. In some cases more products
are returned, such as the maximum and minimun values. Refer to each exercises's
code for more information


## Authors


## License

This project is licensed under the [BSD 3-Clause][99] License.

[1]: https://www.gaia-project.eu
[2]: https://www.raspberrypi.org/
[3]: https://www.dexterindustries.com/grovepi/
[4]: https://electroninks.com/circuit-scribe/
[5]: https://www.seeedstudio.com/Grove-LCD-RGB-Backlight.html
[6]: https://www.seeedstudio.com/Grove-Button.html
[7]: https://www.seeedstudio.com/Grove-Digital-Light-Sensor.html
[8]: https://github.com/GAIA-project/Gaia-Workshop/tree/master/firmware
[9]: https://github.com/DexterInd/GrovePi
[10]: https://pypi.org/project/python-forecastio/
[11]: https://www.sparkworks.net/

[99]: https://github.com/GAIA-project/Gaia-Workshop/blob/master/LICENSE.md
