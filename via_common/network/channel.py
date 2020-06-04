#  Copyright 2019 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

class Channel:
    """
    A simple holder of channel names used with redis
    """
    FROM_CMS = '#CMS'
    ACK_FROM_BROKER = '#BRKOK'
    FROM_BROKER = '#BRK'
    ACK_FROM_CMS = '#CMSOK'
