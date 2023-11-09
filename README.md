# Master's thesis

Title: "Analysis of cybersecurity, performance and building application aspect for different cloud environments"

## Overview

This repository showcases the project component of the master's thesis, where an IoT application will be created. The application will function as a testing platform for assessing the performance of different AWS cloud architectures

**LIST OF CONTENT:**
- [Master's thesis](#masters-thesis)
  - [Overview](#overview)
  - [IoT Application](#iot-application)
    - [Installation](#installation)
    - [Runnig app](#runnig-app)
    - [Checking app output](#checking-app-output)
  - [AWS architectures](#aws-architectures)
    - [Introduction](#introduction)
    - [Installation and usage](#installation-and-usage)
  - [To be done](#to-be-done)
  - [Author](#author)

## IoT Application
Instructions on how to install, run the application, and view the results.

### Installation
To run application on linux device first follow instruction bellow:
1. Create AWS account
2. Install AWS IoT Greengrass Core software on linux device, instruction for this step can be found [here](https://docs.aws.amazon.com/greengrass/v1/developerguide/module2.html)
3. Install AWS Greengrass Cli, instruction for this step can be found [here](https://docs.aws.amazon.com/greengrass/v2/developerguide/install-gg-cli.html)
4. Clone this repository to target device

### Runnig app
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


### Checking app output
If everything was done correctly, messages sent by application can be view using [AWS MQTT test client](https://docs.aws.amazon.com/iot/latest/developerguide/view-mqtt-messages.html)
by subscribing to right mqtt topic (by default "iot_app/all_data" )

## AWS architectures

### Introduction
For the part of the application that uses cloud services, several cloud architecture designs have been prepared. These architectures are saved as AWS CloudFormation templates, which are YAML/JSON files that describe all the necessary resources and their relationships.

### Installation and usage
All AWS CloudFormation templates can be found in "AWS_CF_templates" folder. To view specific architecture open [AWS CloudFormation Designer](https://console.aws.amazon.com/cloudformation/designer) and import chosen template file. To implement the architecture, click the 'Create Stack' button and follow the provided instructions.


## To be done
Things that needs to be done:
- create performance test cases
- choose and design different cloud architectures
- create different cloud architectures
- create unit tests

## Author

[August Majewski](https://github.com/kolovoz14)
