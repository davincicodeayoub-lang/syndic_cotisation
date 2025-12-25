# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Apartment(models.Model):
    _name = 'syndic.apartment'
    _description = 'Appartement / Lot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'num'

    num = fields.Char(
        string='Numéro',
        required=True,
        tracking=True
    )
    type = fields.Selection([
        ('appartement', 'Appartement'),
        ('magasin', 'Magasin'),
        ('bureau', 'Bureau'),
        ('villa', 'Villa'),
        ('autre', 'Autre'),
    ], string='Type', required=True, default='appartement', tracking=True)
    
    building_id = fields.Many2one(
        'syndic.building',
        string='Immeuble',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    residence_id = fields.Many2one(
        'syndic.residence',
        string='Résidence',
        related='building_id.residence_id',
        store=True,
        readonly=True
    )
    
    floor = fields.Integer(
        string='Étage'
    )
    surface = fields.Float(
        string='Surface (m²)'
    )
    nb_rooms = fields.Integer(
        string='Nombre de pièces'
    )
    description = fields.Text(
        string='Description'
    )
    
    # Relations
    person_apartment_ids = fields.One2many(
        'syndic.person.apartment',
        'apartment_id',
        string='Propriétaires'
    )
    
    # Computed fields
    owner_count = fields.Integer(
        string='Nombre de propriétaires',
        compute='_compute_owner_count'
    )
    total_quote_part = fields.Float(
        string='Total quote-part',
        compute='_compute_total_quote_part',
        help='Somme des quotes-parts de tous les propriétaires'
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
    
    @api.depends('num', 'building_id.name', 'type')
    def _compute_display_name(self):
        for record in self:
            type_label = dict(record._fields['type'].selection).get(record.type, '')
            if record.building_id:
                record.display_name = f"{record.building_id.name} - {record.num} ({type_label})"
            else:
                record.display_name = f"{record.num} ({type_label})"
    
    @api.depends('person_apartment_ids')
    def _compute_owner_count(self):
        for record in self:
            record.owner_count = len(record.person_apartment_ids)
    
    @api.depends('person_apartment_ids.quote_part')
    def _compute_total_quote_part(self):
        for record in self:
            record.total_quote_part = sum(
                pa.quote_part for pa in record.person_apartment_ids
            )
    
    @api.constrains('surface')
    def _check_surface(self):
        for record in self:
            if record.surface and record.surface < 0:
                raise ValidationError(_('La surface ne peut pas être négative!'))
    
    @api.constrains('nb_rooms')
    def _check_nb_rooms(self):
        for record in self:
            if record.nb_rooms and record.nb_rooms < 0:
                raise ValidationError(_('Le nombre de pièces ne peut pas être négatif!'))
    
    _sql_constraints = [
        ('num_building_unique', 'UNIQUE(num, building_id)', 
         'Le numéro d\'appartement doit être unique dans l\'immeuble!')
    ]
