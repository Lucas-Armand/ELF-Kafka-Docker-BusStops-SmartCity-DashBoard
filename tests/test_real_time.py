from test_stm_info import url_kafka, url_stm get_vehicle_positions, process_vehicle_postions

while True:
    time.sleep(5)
    get_vehicle_positions(url_stm)
    process_vehicle_postions(url_kafka)



