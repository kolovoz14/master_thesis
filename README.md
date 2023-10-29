# Master's thesis

## "Analysis of cybersecurity, performance and building application aspect for different cloud environments"

## Overview

This repository showcases the project component of the master's thesis, where an IoT application will be created. The application will function as a testing platform for assessing the performance of different AWS cloud architectures

## Installation
To run application on linux device first follow instruction bellow:
1. Create AWS account
2. Install AWS IoT Greengrass Core software on linux device, instruction for this step can be found [here](https://docs.aws.amazon.com/greengrass/v1/developerguide/module2.html)
3. Install AWS Greengrass Cli, instruction for this step can be found [here](https://docs.aws.amazon.com/greengrass/v2/developerguide/install-gg-cli.html)
4. Clone this repository to target device

## Runnig application
Starting and stopping application can be made in two ways:
1. Using bare Greengrass Cli function greengrass-cli deployment create described [here](https://docs.aws.amazon.com/greengrass/v2/developerguide/gg-cli-deployment.html#deployment-create)
2. Using my functions aliases by loading them in bash terminal in repository root folder:

loading function aliases:

```console
. app_functions.sh
```
after that function aliases can be used like this:

```console
start application:
$ app_start
stop application:
$ app_stop
view application logs:
$ app_log
```


### Check application output
If everything was done correctly, messages sent by application can be view using [AWS MQTT test client](https://docs.aws.amazon.com/iot/latest/developerguide/view-mqtt-messages.html)
by subscribing to right mqtt topic (by default "iot_app/all_data" )



## To be done
Things that needs to be done:
- create performance test cases
- choose and design different cloud architectures
- create different cloud architectures
- create unit tests

## Author

[August Majewski](https://github.com/kolovoz14)
