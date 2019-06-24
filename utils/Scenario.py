
class Scenario:

    def __init__(self, xml_file="the xml...",
                 name="the name...",
                 goal="the goal... :)",
                 description="the description...",
                 town="the town...",
                 type="the type...",
                 snapshot="route.mp4",
                 criteria="do not crash at all!",
                 timeout=90
                 ):
        self.xml = xml_file
        self.name = name
        self.type = type
        self.description = description
        self.snapshot = snapshot
        self.goal = goal
        self.town = town
        self.criteria = criteria
        self.timeout = timeout
