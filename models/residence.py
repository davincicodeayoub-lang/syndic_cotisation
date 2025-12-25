# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Residence(models.Model):
    _name = 'syndic.residence'
    _description = 'Residence / Copropriété'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Nom de la résidence',
        required=True,
        tracking=True
    )
    code = fields.Char(
        string='Code',
        tracking=True
    )
    address = fields.Text(
        string='Adresse',
        tracking=True
    )
    city = fields.Char(
        string='Ville',
        tracking=True
    )
    postal_code = fields.Char(
        string='Code postal'
    )
    phone = fields.Char(
        string='Téléphone'
    )
    email = fields.Char(
        string='Email'
    )
    
    # Relations
    building_ids = fields.One2many(
        'syndic.building',
        'residence_id',
        string='Immeubles'
    )
    appel_fond_ids = fields.One2many(
        'syndic.appel.fond',
        'residence_id',
        string='Appels de fonds'
    )
    
    # Computed fields
    building_count = fields.Integer(
        string='Nombre d\'immeubles',
        compute='_compute_building_count'
    )
    apartment_count = fields.Integer(
        string='Nombre d\'appartements',
        compute='_compute_apartment_count'
    )
    owner_count = fields.Integer(
        string='Nombre de propriétaires',
        compute='_compute_owner_count'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    
    @api.depends('building_ids')
    def _compute_building_count(self):
        for record in self:
            record.building_count = len(record.building_ids)
    
    @api.depends('building_ids.apartment_ids')
    def _compute_apartment_count(self):
        for record in self:
            record.apartment_count = sum(
                len(building.apartment_ids) for building in record.building_ids
            )
    
    @api.depends('building_ids.apartment_ids.person_apartment_ids')
    def _compute_owner_count(self):
        for record in self:
            person_ids = set()
            for building in record.building_ids:
                for apartment in building.apartment_ids:
                    for pa in apartment.person_apartment_ids:
                        person_ids.add(pa.person_id.id)
            record.owner_count = len(person_ids)
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Le nom de la résidence doit être unique!')
    ]
