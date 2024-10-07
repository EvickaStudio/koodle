# Filename: config.py

import json
import os

CONFIG_FILE = "config.json"


class Config:
    def __init__(self):
        self.favorites = []
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.favorites = data.get("favorites", [])
        else:
            self.favorites = []

    def save(self):
        data = {"favorites": self.favorites}
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
