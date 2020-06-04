#  Copyright 2019 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import json
import random
import uuid
import zlib
from collections import namedtuple

from via_common.generated.proto.feed_pb2 import DevicePost
from via_common.generated.proto.internal_pb2 import FromBroker, FromCMS


"""
    Helper classes and functions
"""


#
# json helpers
#

def dict2obj(data):
    """
    Helper function for creating the tuple subclasses with well-formed named fields
    """
    return namedtuple('X', (''.join(c if c.isalnum() else '_' for c in x) if not x[0].isnumeric() else 'O' + ''.join(c if c.isalnum() else '_' for c in x)
                            for x in data.keys()))(*data.values())


def json2obj(data):
    """
    Deserialize a str or bytes to a Python object using a helper functions to deduce the object
    attributes
    """
    return json.loads(data, object_hook=dict2obj)


def json2dict(obj):
    """
    Translates a deserialized json object to a dictionary.
    The assumption is that any contained object type has the same class name 'X'.
    """
    res = {}
    if not hasattr(obj, '_fields'):
        return {}  # TODO manage properly errors
    for k in obj._fields:
        v = getattr(obj, k)
        if isinstance(v, str):
            res.update({k: v})
        elif isinstance(v, list):
            res2 = []
            for i in v:
                res2.append(json2dict(i))
            res.update({k: res2})
        elif v.__class__.__name__ == obj.__class__.__name__:
            res.update({k: json2dict(v)})
        # if isinstance(v, str)
    # end for k in obj._fields
    return res


#
# IDs
#

def generate_unique_id():
    """
    Generates a random UUID
    """
    return str(uuid.uuid4())


def get_next_cms_id():
    # TODO aproperway to manage message ID
    return random.getrandbits(32)


def get_next_broker_id():
    # TODO aproperway to manage message ID
    return random.getrandbits(32)


def get_next_internal_id():  # TODO
    # TODO aproperway to manage message ID
    return random.getrandbits(32)


#
# Internal message wrappers
#

def wrap_message(message_id, source_type, message: bytes):
    message_id_b = int(message_id).to_bytes(8, byteorder='little', signed=True)
    source_type_b = int(source_type).to_bytes(4, byteorder='little', signed=True)
    payload = message_id_b + source_type_b
    if message:
        payload += zlib.compress(message)
    # end if message
    return payload


def unwrap_payload(payload: bytes):
    message_id = int.from_bytes(payload[:8], 'little', signed=True)
    source_type = int.from_bytes(payload[8:12], 'little', signed=True)
    try:
        message = zlib.decompress(payload[12:])
    except:
        message = payload[12:]
    return message_id, source_type, message


#
# PROTO Internal
#

def serialize_from_broker(message_id, item_id, item_version, topic, payload: bytes):
    serialized = FromBroker()
    serialized.message_id = message_id
    serialized.item_id = item_id
    serialized.item_version = item_version
    serialized.topic = topic
    serialized.payload = payload
    serialized = serialized.SerializeToString()
    return serialized


def deserialize_from_broker(payload: bytes):
    deserialized = FromBroker()
    deserialized.ParseFromString(payload)
    return deserialized


def serialize_from_cms(message_id, profile_id, subject_id, item_id, item_version, message: bytes):
    serialized = FromCMS()
    serialized.message_id = message_id
    serialized.profile_id = profile_id
    serialized.subject_id = subject_id
    serialized.item_id = item_id
    serialized.item_version = item_version
    serialized.payload = message
    serialized = serialized.SerializeToString()
    return serialized


def deserialize_from_cms(payload: bytes):
    deserialized = FromCMS()
    deserialized.ParseFromString(payload)
    return deserialized


def deserialize_from_cms(payload: bytes):
    deserialized = FromCMS()
    deserialized.ParseFromString(payload)
    return deserialized


#
# PROTO Gateway
#

def serialize_broker_post(broker_post):
    return broker_post.SerializeToString()


def deserialize_device_post(payload):
    deserialized = DevicePost()
    deserialized.ParseFromString(payload)
    return deserialized
