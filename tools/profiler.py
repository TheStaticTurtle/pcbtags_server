import time


class Profiler:
	def __init__(self):
		self.events = []

	def log_event_finished(self, name):
		self.events.append({
			"timestamp": time.time(),
			"name": name
		})

	def start(self):
		self.events = []
		self.events.append({
			"timestamp": time.time(),
			"name": "start"
		})

	def end(self):
		durations = {}
		if self.events[-1]["name"] != "end":
			self.events.append({
				"timestamp": time.time(),
				"name": "end"
			})
		last_event = None
		for event in self.events:
			if last_event is not None:
				durations[event["name"]] = event["timestamp"] - last_event["timestamp"]
				durations[event["name"]] = round(durations[event["name"]] * 1000, 3)
			last_event = event

		tstart = self.events[0]["timestamp"]
		events = []
		for event in self.events:
			event["timestamp"] -= tstart
			event["timestamp"] = round(event["timestamp"] * 1000, 3)
			events.append(event)

		return {
			"events": events,
			"durations": durations,
		}