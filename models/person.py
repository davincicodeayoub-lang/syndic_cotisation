# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class Person(models.Model):
    _name = 'syndic.person'
    _description = 'Personne (Propriétaire / Locataire)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, prenom'

    # Personal Information
    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True
    )
    prenom = fields.Char(
        string='Prénom',
        tracking=True
    )
    type_person = fields.Selection([
        ('proprietaire', 'Propriétaire'),
        ('locataire', 'Locataire'),
        ('gerant', 'Gérant'),
    ], string='Type', default='proprietaire', required=True, tracking=True)
    
    # Identity Documents
    cin = fields.Char(
        string='CIN',
        tracking=True
    )
    passport = fields.Char(
        string='Passeport',
        tracking=True
    )
    
    # Contact Information
    adresse = fields.Text(
        string='Adresse'
    )
    city = fields.Char(
        string='Ville'
    )
    postal_code = fields.Char(
        string='Code postal'
    )
    tel = fields.Char(
        string='Téléphone',
        tracking=True
    )
    mobile = fields.Char(
        string='Mobile'
    )
    email = fields.Char(
        string='Email',
        tracking=True
    )
    
    # Portal Access (Optional)
    login = fields.Char(
        string='Login'
    )
    password = fields.Char(
        string='Mot de passe'
    )
    
    # Company Information (for legal entities)
    is_company = fields.Boolean(
        string='Est une société',
        default=False
    )
    company_name = fields.Char(
        string='Nom de la société'
    )
    ice = fields.Char(
        string='ICE'
    )
    rc = fields.Char(
        string='RC'
    )
    
    # Relations
    apartment_ids = fields.One2many(
        'syndic.person.apartment',
        'person_id',
        string='Appartements'
    )
    reglement_ids = fields.One2many(
        'syndic.reglement',
        'person_id',
        string='Règlements'
    )
    
    # Computed fields
    apartment_count = fields.Integer(
        string='Nombre d\'appartements',
        compute='_compute_apartment_count'
    )
    total_paid = fields.Float(
        string='Total payé',
        compute='_compute_payment_totals'
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
    
    @api.depends('name', 'prenom', 'is_company', 'company_name')
    def _compute_display_name(self):
        for record in self:
            if record.is_company and record.company_name:
                record.display_name = record.company_name
            elif record.prenom:
                record.display_name = f"{record.name} {record.prenom}"
            else:
                record.display_name = record.name
    
    @api.depends('apartment_ids')
    def _compute_apartment_count(self):
        for record in self:
            record.apartment_count = len(record.apartment_ids)
    
    @api.depends('reglement_ids.montant')
    def _compute_payment_totals(self):
        for record in self:
            record.total_paid = sum(
                reglement.montant for reglement in record.reglement_ids
            )
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_regex, record.email):
                    raise ValidationError(_('L\'adresse email n\'est pas valide!'))
    
    @api.constrains('cin', 'passport')
    def _check_identity(self):
        for record in self:
            if not record.cin and not record.passport and not record.is_company:
                raise ValidationError(_('Vous devez fournir au moins un CIN ou un Passeport!'))
    
    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Cet email est déjà utilisé!'),
        ('cin_unique', 'UNIQUE(cin)', 'Ce CIN est déjà utilisé!'),
    ]
