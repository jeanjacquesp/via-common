#  Copyright 2019 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

class SourceType:
    """
        A simple holder of message types
    """
    INVALID = -1
    HEARTBEAT = 0
    ACK = 1
    CMS = 2
    BROKER = 3
    DEVICE = 4
