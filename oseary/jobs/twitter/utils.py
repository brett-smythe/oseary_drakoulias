
# If this service ever moves from a single thread the limits check must changed
# to be more thread safe

class TwitterLimits(object):

    def __init__(self, timeline_rate_reserve=5):
        self.timeline_rate_reserve = timeline_rate_reserve
        self.timeline_requests_left = 0
        self.update_limits()

    def update_limits(self):
        # Api call to get relevant information
        requests_left = 180
        self.timeline_requests_left = requests_left - self.timeline_rate_reserve
        return None


