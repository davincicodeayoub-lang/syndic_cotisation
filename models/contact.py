# -*- coding: utf-8 -*-
from odoo import models, fields

class Contact(models.Model):
    _name = 'syndic.contact'
    _description = 'Contact Urgence / Secondaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    person_id = fields.Many2one(
        'syndic.person',
        string='Personne liée',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    type = fields.Selection([
        ('emergency', 'Urgence'),
        ('secondary', 'Secondaire'),
        ('business', 'Professionnel'),
        ('other', 'Autre'),
    ], string='Type de contact', default='secondary', required=True, tracking=True)

    name = fields.Char(string='Nom complet', required=True, tracking=True)
    phone = fields.Char(string='Téléphone', tracking=True)
    email = fields.Char(string='Email')
    
    relationship = fields.Char(string='Relation (ex: Conjoint, Fils...)')
    is_primary = fields.Boolean(string='Contact principal', default=False)
    
    notes = fields.Text(string='Notes')

    active = fields.Boolean(default=True)
