# Filename: config.py

import json
import os

CONFIG_FILE = "config.json"


class Config:
    def __init__(self):
        self.favorites = []
        self.course_states = {}  # New addition
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.favorites = data.get("favorites", [])
                self.course_states = data.get("course_states", {})
        else:
            self.favorites = []
            self.course_states = {}

    def save(self):
        data = {"favorites": self.favorites, "course_states": self.course_states}
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def add_favorite(self, course_id):
        if course_id not in self.favorites:
            self.favorites.append(course_id)
            self.save()

    def remove_favorite(self, course_id):
        if course_id in self.favorites:
            self.favorites.remove(course_id)
            self.save()

    def update_course_state(self, course_id, state):
        self.course_states[str(course_id)] = state
        self.save()

    def get_course_state(self, course_id):
        return self.course_states.get(str(course_id))
