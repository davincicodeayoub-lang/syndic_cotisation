# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Budget(models.Model):
    _name = 'syndic.budget'
    _description = 'Budget Prévisionnel / Réel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, residence_id'

    residence_id = fields.Many2one(
        'syndic.residence',
        string='Résidence',
        required=True,
        tracking=True
    )
    
    year = fields.Integer(
        string='Année',
        required=True,
        default=lambda self: fields.Date.today().year,
        tracking=True
    )
    
    type = fields.Selection([
        ('previsionnel', 'Prévisionnel'),
        ('reel', 'Réel'),
    ], string='Type de budget', default='previsionnel', required=True, tracking=True)
    
    line_ids = fields.One2many(
        'syndic.budget.line',
        'budget_id',
        string='Lignes budgétaires'
    )
    
    total_amount = fields.Float(
        string='Montant Total',
        compute='_compute_total_amount',
        store=True,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('approved', 'Approuvé'),
        ('closed', 'Clôturé'),
    ], string='État', default='draft', tracking=True)
    
    notes = fields.Text(string='Notes')

    @api.depends('line_ids.planned_amount', 'type')
    def _compute_total_amount(self):
        for record in self:
            # Usually budget totals are based on planned amounts for forecast
            record.total_amount = sum(line.planned_amount for line in record.line_ids)

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_close(self):
        self.write({'state': 'closed'})
    
    def action_draft(self):
        self.write({'state': 'draft'})

    _sql_constraints = [
        ('residence_year_type_unique', 'UNIQUE(residence_id, year, type)', 
         'Un budget de ce type existe déjà pour cette résidence et cette année!')
    ]


class BudgetLine(models.Model):
    _name = 'syndic.budget.line'
    _description = 'Ligne Budgétaire'

    budget_id = fields.Many2one(
        'syndic.budget',
        string='Budget',
        required=True,
        ondelete='cascade'
    )
    
    category_id = fields.Many2one(
        'syndic.charge_category',
        string='Catégorie de charge',
        required=True
    )
    
    description = fields.Char(string='Description')
    
    planned_amount = fields.Float(string='Montant Prévisionnel', required=True, default=0.0)
    actual_amount = fields.Float(string='Montant Réel', default=0.0)
    
    variance = fields.Float(
        string='Écart',
        compute='_compute_variance',
        store=True,
        help="Différence entre Prévu et Réel"
    )

    @api.depends('planned_amount', 'actual_amount')
    def _compute_variance(self):
        for record in self:
            record.variance = record.planned_amount - record.actual_amount
