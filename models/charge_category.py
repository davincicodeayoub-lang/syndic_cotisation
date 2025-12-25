# -*- coding: utf-8 -*-
from odoo import models, fields

class ChargeCategory(models.Model):
    _name = 'syndic.charge_category'
    _description = 'Catégorie de Charges'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'display_name'
    _order = 'code, name'

    name = fields.Char(string='Nom', required=True, translate=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    
    parent_id = fields.Many2one('syndic.charge_category', string='Catégorie Parente', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    
    child_ids = fields.One2many('syndic.charge_category', 'parent_id', string='Sous-catégories')

    type = fields.Selection([
        ('fixe', 'Charges Fixes'),
        ('variable', 'Charges Variables'),
        ('travaux', 'Travaux Exceptionnels'),
        ('autre', 'Autre'),
    ], string='Type', default='fixe', required=True)

    is_repartition_key_required = fields.Boolean(string='Clé de répartition requise', default=False)
    
    active = fields.Boolean(default=True)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    def _compute_display_name(self):
        for record in self:
            if record.code:
                record.display_name = f"[{record.code}] {record.name}"
            else:
                record.display_name = record.name

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code de catégorie doit être unique!')
    ]
