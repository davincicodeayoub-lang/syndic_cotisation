# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AppelFond(models.Model):
    _name = 'syndic.appel.fond'
    _description = 'Appel de Fonds / Cotisation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_emission desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau')
    )
    libelle = fields.Char(
        string='Libellé',
        required=True,
        tracking=True
    )
    description = fields.Text(
        string='Description'
    )

    # Financial
    montant = fields.Float(
        string='Montant de base',
        required=True,
        tracking=True,
        help='Montant de base qui sera multiplié par la quote-part'
    )
    montant_total = fields.Float(
        string='Montant total',
        compute='_compute_montant_total',
        store=True,
        help='Montant total à collecter (somme de tous les appartements)'
    )

    # Périodicité
    periode = fields.Selection([
        ('unique', 'Unique'),
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('semestriel', 'Semestriel'),
        ('annuel', 'Annuel'),
    ], string='Périodicité', default='mensuel', required=True, tracking=True)

    # Type
    type_charge = fields.Selection([
        ('generale', 'Charge générale'),
        ('entretien', 'Entretien'),
        ('travaux', 'Travaux'),
        ('provision', 'Provision'),
        ('exceptionnelle', 'Charge exceptionnelle'),
    ], string='Type de charge', default='generale', required=True, tracking=True)

    # Relations
    residence_id = fields.Many2one(
        'syndic.residence',
        string='Résidence',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    # Dates
    date_emission = fields.Date(
        string='Date d\'émission',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    date_echeance = fields.Date(
        string='Date d\'échéance',
        tracking=True
    )
    annee = fields.Integer(
        string='Année',
        default=lambda self: fields.Date.today().year,
        required=True
    )
    mois = fields.Selection([
        ('01', 'Janvier'),
        ('02', 'Février'),
        ('03', 'Mars'),
        ('04', 'Avril'),
        ('05', 'Mai'),
        ('06', 'Juin'),
        ('07', 'Juillet'),
        ('08', 'Août'),
        ('09', 'Septembre'),
        ('10', 'Octobre'),
        ('11', 'Novembre'),
        ('12', 'Décembre'),
    ], string='Mois')

    # Status
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('confirme', 'Confirmé'),
        ('envoye', 'Envoyé'),
        ('annule', 'Annulé'),
    ], string='État', default='brouillon', tracking=True)

    # Computed fields
    nb_apartments = fields.Integer(
        string='Nombre d\'appartements',
        compute='_compute_nb_apartments'
    )
    montant_collecte = fields.Float(
        string='Montant collecté',
        compute='_compute_montant_collecte'
    )
    taux_collecte = fields.Float(
        string='Taux de collecte (%)',
        compute='_compute_taux_collecte'
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    # Notes
    notes = fields.Text(
        string='Notes'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('syndic.appel.fond') or _('Nouveau')
        return super(AppelFond, self).create(vals)

    @api.depends('residence_id')
    def _compute_nb_apartments(self):
        for record in self:
            if record.residence_id:
                record.nb_apartments = sum(
                    len(building.apartment_ids)
                    for building in record.residence_id.building_ids
                )
            else:
                record.nb_apartments = 0

    @api.depends('montant', 'residence_id')
    def _compute_montant_total(self):
        for record in self:
            total = 0.0
            if record.residence_id:
                for building in record.residence_id.building_ids:
                    for apartment in building.apartment_ids:
                        for pa in apartment.person_apartment_ids:
                            total += record.montant * pa.quote_part
            record.montant_total = total

    def _compute_montant_collecte(self):
        """Montant déjà encaissé pour cet appel de fonds."""
        # À finaliser : somme des règlements au statut 'encaisse'
        for rec in self:
            rec.montant_collecte = sum(
                reg.montant for reg in rec.reglement_ids
                if reg.state == 'encaisse'
            )

    @api.depends('montant_total', 'montant_collecte')
    def _compute_taux_collecte(self):
        for record in self:
            record.taux_collecte = (
                (record.montant_collecte / record.montant_total * 100)
                if record.montant_total else 0.0
            )

    # Actions
    def action_confirm(self):
        self.write({'state': 'confirme'})

    def action_send(self):
        self.write({'state': 'envoye'})

    def action_cancel(self):
        self.write({'state': 'annule'})

    def action_draft(self):
        self.write({'state': 'brouillon'})

    # Contraintes
    @api.constrains('montant')
    def _check_montant(self):
        for record in self:
            if record.montant <= 0:
                raise ValidationError(_('Le montant doit être supérieur à zéro!'))

    @api.constrains('date_emission', 'date_echeance')
    def _check_dates(self):
        for record in self:
            if record.date_echeance and record.date_emission:
                if record.date_echeance < record.date_emission:
                    raise ValidationError(_('La date d\'échéance doit être postérieure à la date d\'émission!'))