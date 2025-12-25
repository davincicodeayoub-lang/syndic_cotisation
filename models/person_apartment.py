# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PersonApartment(models.Model):
    _name = 'syndic.person.apartment'
    _description = 'Liaison Personne - Appartement (Copropriété)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    person_id = fields.Many2one(
        'syndic.person',
        string='Personne',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    apartment_id = fields.Many2one(
        'syndic.apartment',
        string='Appartement',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    # Ownership details
    part = fields.Float(
        string='Part (%)',
        help='Pourcentage de propriété de cet appartement',
        default=100.0,
        tracking=True
    )
    quote_part = fields.Float(
        string='Quote-part',
        help='Quote-part pour le calcul des charges',
        required=True,
        tracking=True
    )

    # Status
    statut = fields.Selection([
        ('proprietaire', 'Propriétaire'),
        ('locataire', 'Locataire'),
        ('usufruitier', 'Usufruitier'),
        ('nu_proprietaire', 'Nu-propriétaire'),
    ], string='Statut', default='proprietaire', required=True, tracking=True)

    # Dates
    date_acquisition = fields.Date(
        string='Date d\'acquisition'
    )
    date_debut = fields.Date(
        string='Date de début',
        default=fields.Date.today
    )
    date_fin = fields.Date(
        string='Date de fin'
    )

    # Related fields used in kanban / search  →  store=True
    residence_id = fields.Many2one(
        'syndic.residence',
        string='Résidence',
        related='apartment_id.residence_id',
        store=True,          # ← kanban safe
        readonly=True
    )
    building_id = fields.Many2one(
        'syndic.building',
        string='Immeuble',
        related='apartment_id.building_id',
        store=True,          # ← kanban safe
        readonly=True
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    # Notes
    notes = fields.Text(
        string='Notes'
    )

    # Display name
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True
    )

    @api.depends('person_id.name', 'apartment_id.num', 'statut')
    def _compute_display_name(self):
        for record in self:
            statut_label = dict(record._fields['statut'].selection).get(record.statut, '')
            if record.person_id and record.apartment_id:
                record.display_name = f"{record.person_id.display_name} - {record.apartment_id.display_name} ({statut_label})"
            else:
                record.display_name = f"{statut_label}"

    # ------------------- existing constraints / onchanges -------------------
    @api.constrains('part')
    def _check_part(self):
        for record in self:
            if record.part < 0 or record.part > 100:
                raise ValidationError(_('La part doit être entre 0 et 100%!'))

    @api.constrains('quote_part')
    def _check_quote_part(self):
        for record in self:
            if record.quote_part < 0:
                raise ValidationError(_('La quote-part ne peut pas être négative!'))

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_debut and record.date_fin:
                if record.date_fin < record.date_debut:
                    raise ValidationError(_('La date de fin doit être postérieure à la date de début!'))

    @api.constrains('person_id', 'apartment_id', 'date_debut', 'date_fin')
    def _check_overlapping_periods(self):
        """Vérifie qu'il n'y a pas de périodes qui se chevauchent pour la même personne et le même appartement"""
        for record in self:
            if not record.date_debut:
                continue

            domain = [
                ('id', '!=', record.id),
                ('person_id', '=', record.person_id.id),
                ('apartment_id', '=', record.apartment_id.id),
                ('date_debut', '<=', record.date_fin or '2099-12-31'),
            ]

            if record.date_fin:
                domain.append(('date_fin', '>=', record.date_debut))

            overlapping = self.search(domain, limit=1)
            if overlapping:
                raise ValidationError(_(
                    'Il existe déjà une période qui chevauche pour cette personne et cet appartement!'
                ))

    _sql_constraints = [
        ('person_apartment_unique', 'UNIQUE(person_id, apartment_id, date_debut)',
         'Cette liaison existe déjà pour cette date!')
    ]