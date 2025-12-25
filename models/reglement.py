# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Reglement(models.Model):
    _name = 'syndic.reglement'
    _description = 'Règlement / Paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, num_recu desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau')
    )
    num_recu = fields.Char(
        string='N° Reçu',
        tracking=True
    )

    # Payer
    person_id = fields.Many2one(
        'syndic.person',
        string='Personne',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    apartment_id = fields.Many2one(
        'syndic.apartment',
        string='Appartement',
        tracking=True
    )

    # Payment details
    mode = fields.Selection([
        ('espece', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement bancaire'),
        ('carte', 'Carte bancaire'),
        ('prelevement', 'Prélèvement'),
        ('autre', 'Autre'),
    ], string='Mode de paiement', required=True, default='espece', tracking=True)

    date = fields.Date(
        string='Date de paiement',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    montant = fields.Float(
        string='Montant',
        required=True,
        tracking=True
    )

    # Chèque details
    num_cheque = fields.Char(string='N° Chèque')
    banque       = fields.Char(string='Banque')
    date_encaissement = fields.Date(string='Date d\'encaissement')

    # Virement details
    reference_virement = fields.Char(string='Référence virement')

    # Linked to Appel de Fonds
    appel_fond_id = fields.Many2one(
        'syndic.appel.fond',
        string='Appel de fonds',
        tracking=True
    )
    residence_id = fields.Many2one(
        'syndic.residence',
        string='Résidence',
        related='appel_fond_id.residence_id',
        store=True,
        readonly=True
    )

    # Status
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('encaisse', 'Encaissé'),
        ('rejete', 'Rejeté'),
        ('annule', 'Annulé'),
    ], string='État', default='brouillon', tracking=True)

    # Notes
    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Actif', default=True)

    # Printed
    is_printed = fields.Boolean(string='Imprimé', default=False)

    _sql_constraints = [
        ('reglement_name_unique', 'UNIQUE(name)', 'La référence du règlement doit être unique!')
    ]

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model
    def create(self, vals):
        # Référence
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = (
                self.env['ir.sequence'].next_by_code('syndic.reglement') or
                _('Nouveau')
            )

        # Numéro de reçu : uniquement la séquence (pas de fallback unsafe)
        if not vals.get('num_recu'):
            vals['num_recu'] = self.env['ir.sequence'].next_by_code('syndic.reglement.recu')

        return super(Reglement, self).create(vals)

    # ------------------------------------------------------------------
    # ONCHANGE
    # ------------------------------------------------------------------
    @api.onchange('person_id')
    def _onchange_person_id(self):
        """Si la personne n'a qu'un seul appartement, le sélectionner automatiquement"""
        if self.person_id and len(self.person_id.apartment_ids) == 1:
            self.apartment_id = self.person_id.apartment_ids[0].apartment_id
        else:
            self.apartment_id = False

    @api.onchange('mode')
    def _onchange_mode(self):
        """Réinitialiser les champs spécifiques au mode de paiement"""
        if self.mode != 'cheque':
            self.num_cheque = False
            self.banque = False
            self.date_encaissement = False
        if self.mode != 'virement':
            self.reference_virement = False

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------
    def action_validate(self):
        self.write({'state': 'valide'})

    def action_encaisse(self):
        if self.mode == 'cheque' and not self.date_encaissement:
            self.date_encaissement = fields.Date.today()
        self.write({'state': 'encaisse'})

    def action_reject(self):
        self.write({'state': 'rejete'})

    def action_cancel(self):
        self.write({'state': 'annule'})

    def action_draft(self):
        self.write({'state': 'brouillon'})

    def action_print_receipt(self):
        """Imprimer le reçu de paiement"""
        self.write({'is_printed': True})
        return self.env.ref('syndic_cotisation.action_report_reglement_receipt').report_action(self)

    # ------------------------------------------------------------------
    # CONTRAINTES
    # ------------------------------------------------------------------
    @api.constrains('montant')
    def _check_montant(self):
        for record in self:
            if record.montant <= 0:
                raise ValidationError(_('Le montant doit être supérieur à zéro!'))

    @api.constrains('date', 'date_encaissement')
    def _check_dates(self):
        for record in self:
            if record.date_encaissement and record.date:
                if record.date_encaissement < record.date:
                    raise ValidationError(_('La date d\'encaissement ne peut pas être antérieure à la date de paiement!'))

    @api.constrains('mode', 'num_cheque')
    def _check_cheque(self):
        for record in self:
            if record.mode == 'cheque' and record.state in ['valide', 'encaisse']:
                if not record.num_cheque:
                    raise ValidationError(_('Le numéro de chèque est obligatoire pour ce mode de paiement!'))