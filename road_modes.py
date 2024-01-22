class RoadMode:
    """
    Класс режима игры. Создан для легкого добавления новвых режимов без изменения основного кода
    """
    def __init__(self,
                 traffic_lanes_forward_count,
                 traffic_lanes_back_count,
                 traffic_lane_width=80,
                 sidewalk_width=50, road_marking_width=5):
        self.road_marking_width = road_marking_width
        self.traffic_lane_width = traffic_lane_width
        self.traffic_lanes_forward_count = traffic_lanes_forward_count
        self.traffic_lanes_back_count = traffic_lanes_back_count
        self.range_x = (
            sidewalk_width,
            sidewalk_width + traffic_lane_width * (traffic_lanes_forward_count + traffic_lanes_back_count))
        self.road_marking_coords_x = [sidewalk_width + i * traffic_lane_width - self.road_marking_width * 0.5 for i in
                                      range(1, traffic_lanes_forward_count + traffic_lanes_back_count)]
        self.back_cars_coords_x = [sidewalk_width + i * traffic_lane_width for i in
                              range(traffic_lanes_back_count)]
        self.forward_cars_coords_x = [sidewalk_width + i * traffic_lane_width for i in
                              range(traffic_lanes_back_count, traffic_lanes_forward_count + traffic_lanes_back_count)]
        self.screen_width = sidewalk_width * 2 + traffic_lane_width * (traffic_lanes_forward_count + traffic_lanes_back_count)

    def get_player_x_coord(self):
        # Этот метод будет переопределен в дочерних классах, когда будут точно известны координаты полос
        pass


class FourLinesBackForLinesForwardMode(RoadMode):
    """
    Четыре полосы в обе стороны
    """
    def __init__(self):
        super().__init__(traffic_lanes_forward_count=4, traffic_lanes_back_count=4)

    def get_player_x_coord(self):
        return self.forward_cars_coords_x[1]


class EightLinesForwardMode(RoadMode):
    """
    8 полос в одну сторону
    """
    def __init__(self):
        super().__init__(traffic_lanes_forward_count=8, traffic_lanes_back_count=0)

    def get_player_x_coord(self):
        return self.forward_cars_coords_x[3]

