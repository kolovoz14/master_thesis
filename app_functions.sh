#!/bin/bash

export COMPONENT_NAME="com.iot_app"
export COMPONENT_VERSION="1.1.0"
export RECIPE_DIR="./components/recipe"
export ARTIFACT_DIR="./components/artifacts"
export GREENGRASS_CLI_PATH="/greengrass/v2/bin/greengrass-cli"
export GREENGRASS_ROOT_PATH="/greengrass/v2"

app_start(){ sudo $GREENGRASS_CLI_PATH deployment create --recipeDir $RECIPE_DIR --artifactDir $ARTIFACT_DIR --merge "$COMPONENT_NAME=$COMPONENT_VERSION"; }
app_stop(){ sudo $GREENGRASS_CLI_PATH --ggcRootPath $GREENGRASS_ROOT_PATH deployment create --remove "$COMPONENT_NAME";}

app_log(){ sudo tail -f $GREENGRASS_ROOT_PATH/logs/$COMPONENT_NAME.log; }
app_log_all(){ sudo cat $GREENGRASS_ROOT_PATH/logs/$COMPONENT_NAME.log; }
gg_log(){ sudo tail -f $GREENGRASS_ROOT_PATH/logs/greengrass.log; }
gg_log_all(){ sudo cat $GREENGRASS_ROOT_PATH/logs/greengrass.log; }

app_restart()
{
  app_stop;
  app_start;
  app_log;
}

