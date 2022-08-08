from influxdb import InfluxDBClient
client = InfluxDBClient(host='localhost', port=8086, username='admin', password='xxx')
client.switch_database('selectronic')
client.query('SELECT last(*) FROM "selectronic"')

