class RoadMode:
    def __init__(self,
                 traffic_lanes_forward_count,
                 traffic_lanes_back_count,
                 traffic_lane_width=125,
                 sidewalk_width=75, road_marking_width=10):
        self.traffic_lanes_forward_count = traffic_lanes_forward_count
        self.traffic_lanes_back_count = traffic_lanes_back_count
        self.range_x = (
            sidewalk_width,
            sidewalk_width + traffic_lane_width * (traffic_lanes_forward_count + traffic_lanes_back_count))
        self.road_marking_coords_x = [sidewalk_width + i * traffic_lane_width - road_marking_width * 0.5 for i in
                                      range(1, traffic_lanes_forward_count + traffic_lanes_back_count)]
        self.cars_coords_x = [sidewalk_width + i * traffic_lane_width for i in
                              range(traffic_lanes_forward_count + traffic_lanes_back_count)]

        self.screen_width = sidewalk_width * 2 + traffic_lane_width * (traffic_lanes_forward_count + traffic_lanes_back_count)

    def get_player_x_coord(self):
        pass


class TwoLanesForwardTwoLanesBackMode(RoadMode):
    def __init__(self):
        super().__init__(traffic_lanes_forward_count=2, traffic_lanes_back_count=2)

    def get_player_x_coord(self):
        return self.cars_coords_x[2]