# -*- coding: utf-8 -*-
{
    'name': 'Syndic Cotisation',
    'version': '17.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Gestion des copropriétés et cotisations',
    'description': """
Module de gestion de syndic pour:
===================================
* Résidences et immeubles
* Propriétaires et locataires
* Appartements et quotes-parts
* Appels de fonds
* Règlements et paiements

Features:
---------
* Multi-résidence management
* Owner and tenant tracking
* Quote-part calculation
* Payment management
* Receipt printing
* Financial reporting
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'external_dependencies': {
        'python': ['dateutil'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Actions  ( MUST be loaded before any view that uses them )
        'views/actions.xml',

        # Data
        'data/sequences.xml',

        # Views  (actions before menus!)
        'views/residence_views.xml',
        'views/building_views.xml',
        'views/apartment_views.xml',
        'views/person_views.xml',
        'views/person_apartment_views.xml',
        'views/appel_fond_views.xml',
        'views/reglement_views.xml',

        # Menu last
        'views/menu.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 10,
}