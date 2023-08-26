# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class Car(models.Model):
    _name = 'odoo_model_advanced.car'
    _description = 'Coche'

    name = fields.Char(string='Modelo')
    number_plate = fields.Char(string='Matrícula')
    cv = fields.Float(string='CV')
    colour = fields.Char(string='Color')
    fuel_litres = fields.Float(string='Litros')

    def filter(self):
        cars = self.env['odoo_model_advanced.car'].search([])
        cars_filtered = cars.filtered(lambda c: c.cv >= 90)
        self.print_cars(cars_filtered)

    def print_cars(self, cars):
        for car in cars:
            print(car.name, car.cv, car.fuel_litres)











