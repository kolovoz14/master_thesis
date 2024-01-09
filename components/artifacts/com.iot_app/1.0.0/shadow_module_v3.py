import json
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    GetThingShadowRequest,
    UpdateThingShadowRequest,
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    PublishMessage,
    BinaryMessage,
    PublishToTopicRequest,
    SubscribeToTopicRequest,
    GetThingShadowRequest,
    UpdateThingShadowRequest,
)

import logging
import collections.abc


### THIS MODULE LETS OTHER GREENGRASS APPS USE THING SHADOWS

logger = logging.getLogger(__name__)

class StreamHandlerShadow(client.SubscribeToTopicStreamHandler):  # receives messages with Shadow Manager settings - in this case periodically every 60 sec.
    topic=""
    message_queue=[]
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        logger.info("received shadow delta message")
        try:
            message_str = str(event.binary_message.message, "utf-8")
            #logger.info(str(type(message_str)))
            self.message_queue.append(message_str)

        except Exception as e:
                logger.error(str(e))

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        logger.warn("stream_error, stream will be closed")
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        logger.warning("stream closed")
        pass


def start_subscribing(topic,ipc_client:client.GreengrassCoreIPCClient,StreamHandler,timeout=5): # sub local pub/sub

    request = SubscribeToTopicRequest()
    request.topic = topic
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_topic(handler)
    operation.activate(request)
    future_response = operation.get_response()
    future_response.result(timeout)
    logger.info("started subscribing to "+str(topic))
    return handler

def send_request(topic,json_message,ipc_client,timeout=5):
    request = PublishToTopicRequest()
    request.topic = topic
    publish_message = PublishMessage()
    publish_message.binary_message = BinaryMessage()
    str_message=json.dumps(json_message)
    publish_message.binary_message.message = bytes(str_message, "utf-8")
    request.publish_message = publish_message
    operation = ipc_client.new_publish_to_topic()
    operation.activate(request)
    future_response = operation.get_response()
    future_response.result(timeout)


def get_thing_shadow(ipc_client:client.GreengrassCoreIPCClient,thingName, shadowName,timeout=5): # get local shadow
    try:
        get_thing_shadow_request = GetThingShadowRequest()
        get_thing_shadow_request.thing_name = thingName
        get_thing_shadow_request.shadow_name = shadowName

        op = ipc_client.new_get_thing_shadow()
        op.activate(get_thing_shadow_request)
        future = op.get_response()
        result = future.result(timeout)
        jsonmsg = json.loads(result.payload)

        return jsonmsg
    except Exception as e:
        logger.error("Error get shadow "+str(type(e))+str(e))
        return {}


def update_thing_shadow(ipc_client:client.GreengrassCoreIPCClient,thingName, shadowName, payload,timeout=5): # update local shadow
    try:
        # create the UpdateThingShadow request
        update_thing_shadow_request = UpdateThingShadowRequest()
        update_thing_shadow_request.thing_name = thingName
        update_thing_shadow_request.shadow_name = shadowName
        update_thing_shadow_request.payload = payload

        # retrieve the UpdateThingShadow response after sending the request to the IPC server
        op = ipc_client.new_update_thing_shadow()
        op.activate(update_thing_shadow_request)
        fut = op.get_response()

        result = fut.result(timeout)
        return result.payload

    except Exception as e:
        logger.error("Error get shadow "+str(type(e))+str(e))
        # except ConflictError | UnauthorizedError | ServiceError

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def update_shadow_with_delta(ipc_client:client.GreengrassCoreIPCClient,shadow:dict,thing_name:str,shadow_name:str,subscription_handler:StreamHandlerShadow):  #deleting fields in cloud device shadow is done by setting field value to "null"
    temp_shadow=shadow
    try:
        logger.debug("new shadow mess: updating shadow "+shadow_name+" file")
        shadow_str=subscription_handler.message_queue.pop(0)
        logger.debug("delta update str: "+str(shadow_str))
        shadow_update=json.loads(shadow_str)
        shadow=deep_update(shadow,shadow_update['state']) # deep update nested dict!!!
        logger.info("updated shadow "+shadow_name+" : "+str(shadow))
        currentstate={'state':{}}
        currentstate['state']['reported']=shadow
        update_thing_shadow(ipc_client,thing_name,shadow_name,payload=bytes(json.dumps(currentstate), "utf-8")) # update local shadow
        return shadow
    except Exception as e:
        logger.warning("error while updating shadow "+shadow_name+" : "+str(e))
        return temp_shadow


def get_initial_shadow(ipc_client:client.GreengrassCoreIPCClient,thing_name,shadow_name:str,shadow_update_topic:str):
    full_shadow = get_thing_shadow(ipc_client,thing_name,shadow_name)
    try:
        shadow=full_shadow['state']['desired']  # here deleted fields are applied to shadow
        logger.debug("desired and actual shadow: "+str(shadow))
        if(shadow=={}): #handle error while getting thing shadow
            logger.error("can not get shadow from device shadow")
            return {}
        else:
            try:
                report_shadow=remove_deleted_fields_from_shadow(full_shadow['state']['desired'],full_shadow['state']['reported'])
            except:
                logger.info("deleted fields were not removed")
                report_shadow=shadow
            currentstate={'state':{}}
            currentstate['state']['reported']=report_shadow
            update_shadow_result=update_thing_shadow(ipc_client,thing_name,shadow_name,payload=bytes(json.dumps(currentstate), "utf-8"))
            send_request(topic=shadow_update_topic,json_message=currentstate,ipc_client=ipc_client) # send request to cloud shadow to sync reported state
    except Exception as e:
        logger.warning("error while obtaining shadow from local thing"+str(e))
        return {}
    return shadow


def remove_deleted_fields_from_shadow(desired_shadow,reported_shadow):
    for key in reported_shadow:
        if(type(reported_shadow[key])==dict):
            try:
                reported_shadow[key]=remove_deleted_fields_from_shadow(desired_shadow[key],reported_shadow[key])    # delete fields for nested dicts
            except:
                logger.exception("error while removing nested field")
        if key not in desired_shadow:
            reported_shadow[key]=None
            logger.warning("changed key: "+str(key)+" to None")
    logger.debug("shadow reported to shadow:"+str(reported_shadow))
    return reported_shadow

def get_device_shadow_config(ipc_client,thing_name,shadow_config_name):
    ### get initial config from shadow, update reported state
    shadow_config_update_topic="$aws/things/"+thing_name+"/shadow/name/"+shadow_config_name+"/update"
    logger.info("shadow_config_name "+shadow_config_name)
    config=get_initial_shadow(ipc_client,thing_name,shadow_config_name,shadow_config_update_topic)

    return config

def subscribe_to_config_delta(ipc_client,thing_name,shadow_config_name):
    ### start subscribing to default shadow delta topic
    shadow_config_delta_topic="$aws/things/"+thing_name+"/shadow/name/"+shadow_config_name+"/update/delta"
    shadow_config_sub_handler=start_subscribing(shadow_config_delta_topic,ipc_client=ipc_client,StreamHandler=StreamHandlerShadow)

    return shadow_config_sub_handler