# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Building(models.Model):
    _name = 'syndic.building'
    _description = 'Immeuble / Bâtiment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Nom de l\'immeuble',
        required=True,
        tracking=True
    )
    code = fields.Char(
        string='Code',
        tracking=True
    )
    residence_id = fields.Many2one(
        'syndic.residence',
        string='Résidence',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    address = fields.Text(
        string='Adresse'
    )
    nb_floors = fields.Integer(
        string='Nombre d\'étages',
        default=1
    )
    construction_year = fields.Char(
        string='Année de construction'
    )
    
    # Relations
    apartment_ids = fields.One2many(
        'syndic.apartment',
        'building_id',
        string='Appartements'
    )
    
    # Computed fields
    apartment_count = fields.Integer(
        string='Nombre d\'appartements',
        compute='_compute_apartment_count'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    
    # Display name
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True
    )
    
    @api.depends('name', 'residence_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.residence_id:
                record.display_name = f"{record.residence_id.name} - {record.name}"
            else:
                record.display_name = record.name
    
    @api.depends('apartment_ids')
    def _compute_apartment_count(self):
        for record in self:
            record.apartment_count = len(record.apartment_ids)
    
    @api.constrains('nb_floors')
    def _check_nb_floors(self):
        for record in self:
            if record.nb_floors < 0:
                raise ValidationError(_('Le nombre d\'étages ne peut pas être négatif!'))
    
    _sql_constraints = [
        ('name_residence_unique', 'UNIQUE(name, residence_id)', 
         'Le nom de l\'immeuble doit être unique dans la résidence!')
    ]
