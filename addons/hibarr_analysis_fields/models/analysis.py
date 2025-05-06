from odoo import models, fields, api
from odoo.exceptions import UserError
from lxml import etree

class MultipleSalesperson(models.Model):
    _name = 'multiple.salesperson'
    _description = 'Salesperson for Lead'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    user_id = fields.Many2one('res.users', string='Salesperson')
    commission = fields.Float(string='Commission', default=0.0)

class ResUsers(models.Model):
    _inherit = 'res.users'

    commission = fields.Float(string='Commission', default=0.0, help='Commission percentage for the user.', digits=(5, 2))
    
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_id = fields.Many2one('res.partner', string='Partner')  
    user_ids = fields.Many2many(
        'res.users',
        string='Additional Salespersons',
        relation='crm_lead_user_rel',  
        column1='lead_id',
        column2='user_id',
        tracking=True
    )

    customer_email = fields.Char(
        string="Email",
        related='partner_id.email',
        store=True,
        help="Customer email address",
        readonly=False
    )
    phone = fields.Char(
        string="Phone",
        related='partner_id.phone',
        store=True,
    )
    street = fields.Char(
        string="Street",
        related='partner_id.street',
        store=True,
    )
    city = fields.Char(
        string="City",
        related='partner_id.city',
        store=True,
    )
    zip = fields.Char(
        string="ZIP",
        related='partner_id.zip',
        store=True,
    )
    country_id = fields.Many2one(
        'res.country',
        string="Country",
        related='partner_id.country_id',
        store=True,
    )

    
    #customer information
    referral_source = fields.Many2one('res.partner', string="Referral Source", help="Select the person or company who referred this lead")
    referees_commission = fields.Float(string="Commission", digits=(5, 2))
    sales_commission_percent = fields.Float(string="Commission", digits=(5, 2))
    customer_nationality = fields.Many2one('res.country', string="Customer Nationality")
    vip_status = fields.Selection([
        ('none', 'None'),
        ('vip', 'VIP Package'),
        ('free', 'Free Package')
    ], string="Client Package", default='none')

    bank_services = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Bank Services Required", default='no')

    is_bank_services_readonly = fields.Boolean(
        string="Is Bank Services Readonly",
        compute="_compute_is_bank_services_readonly",
        store=False
    )
    
    lead_quality = fields.Selection(
        selection=[
            ('0', 'Very Low'),
            ('1', 'Low'),
            ('2', 'Medium'),
            ('3', 'High'),
            ('4', 'Very High'),
            ('5', 'Excellent')
        ],
        string='Lead Quality',
        index=True,
        default='0',  
        help="Use this to prioritize your leads: the higher the priority, the more important the lead."
    )
    #personal information
    employment_status = fields.Selection(
        related='partner_id.employment_status',
        string="Employment Status",
        store=True,
        readonly=False
    )
    employment_status_other = fields.Char(
        string="Other Employment Status", 
        help="Please specify if 'Other' is selected",
        related='partner_id.employment_status_other',
        store=True,
        readonly=False
    )
    occupation = fields.Char(
        string="Occupation",
        related='partner_id.occupation',
        store=True,
        readonly=False
    )
    
    # Income fields with currency
    income = fields.Float(
        string="Income",
        digits=(16, 2),
        related='partner_id.income',
        store=True,
        readonly=False
    )
    
    additional_income = fields.Float(
        string="Additional Income", 
        digits=(16, 2),
        related='partner_id.additional_income',
        store=True,
        readonly=False
    )
    
    languages = fields.Many2many(
        comodel_name='custom.language',
        relation='crm_lead_custom_language_rel',
        column1='lead_id',           
        column2='language_id',       
        related='partner_id.languages',
        string="Languages",
        store=True,
        readonly=False,
        help="Languages spoken by the partner."
    )




    marital_status = fields.Selection(
        related='partner_id.marital_status',
        store=True,
        readonly=False
    )
    

    # #partner information
    partner_first_name = fields.Char(
        string="Partner First Name",
        related='partner_id.partner_first_name',
        store=True,
        readonly=False
    )
    partner_last_name = fields.Char(
        string="Partner Last Name",
        related='partner_id.partner_last_name',
        store=True,
        readonly=False
    )
    partner_nationality = fields.Many2one(
        'res.country',
        string="Partner Nationality",
        related='partner_id.partner_nationality',
        store=True,
        readonly=False
    )
    partner_city = fields.Char(
        string="Partner City",
        related='partner_id.partner_city',
        store=True,
        readonly=False
    )
    partner_country = fields.Many2one(
        string="Partner Country",
        related='partner_id.partner_country',
        store=True,
        readonly=False
    )
    partner_employment_status = fields.Selection(
        related='partner_id.partner_employment_status',
        store=True,
        readonly=False
    )
    partner_employment_status_other = fields.Char(
        string="Other Partner Employment Status",
        related='partner_id.partner_employment_status_other',
        store=True,
        readonly=False
    )
    partner_occupation = fields.Char(
        string="Partner Occupation",
        related='partner_id.partner_occupation',
        store=True,
        readonly=False
    )
    # # Partner Income fields with currency
    partner_income = fields.Float(
        string="Partner Income",
        digits=(16, 2),
        related='partner_id.partner_income',
        store=True,
        readonly=False
    )
    
    
    partner_additional_income = fields.Float(
        string="Partner Additional Income",
        digits=(16, 2),
        related='partner_id.partner_additional_income',
        store=True,
        readonly=False
    )
    
    partner_languages = fields.Many2many(
        comodel_name='custom.language',
        relation='crm_lead_custom_language_rel',
        column1='lead_id',           # name of FK pointing to crm.lead
        column2='language_id',       # name of FK pointing to custom.language
        related='partner_id.partner_languages',
        string="Partner Languages",
        store=True,
        readonly=False,
        help="Languages spoken by the partner."
    )

    
    # #children information
    children_group = fields.Selection(
        related='partner_id.children_group',
        store=True,
        readonly=False
    )

    age = fields.Integer(
        string="Child 1 Age",
        related='partner_id.age',
        store=True,
        readonly=False
    )
    gender = fields.Selection(
        related='partner_id.gender',
        store=True,
        readonly=False
    )

    age2 = fields.Integer(
        string="Child 2 Age",
        related='partner_id.age2',
        store=True,
        readonly=False
    )
    gender2 = fields.Selection(
        related='partner_id.gender2',
        store=True,
        readonly=False
    )

    age3 = fields.Integer(
        string="Child 3 Age",
        related='partner_id.age3',
        store=True,
        readonly=False
    )
    gender3 = fields.Selection(
        related='partner_id.gender3',
        store=True,
        readonly=False
    )

    age4 = fields.Integer(
        string="Child 4 Age",
        related='partner_id.age4',
        store=True,
        readonly=False
    )
    gender4 = fields.Selection(
        related='partner_id.gender4',
        store=True,
        readonly=False
    )

    age5 = fields.Integer(
        string="Child 5 Age",
        related='partner_id.age5',
        store=True,
        readonly=False
    )
    gender5 = fields.Selection(
        related='partner_id.gender5',
        store=True,
        readonly=False
    )
        
    personal_question1 = fields.Selection(
        related='partner_id.personal_question1',
        store=True,
        readonly=False
    )

    #customer experience
    customer_experience_one = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Have you been to North Cyprus? ?")
    customer_experience_two = fields.Char(string="How many times have you been to North Cyprus?")
    customer_experience_three = fields.Date(string="Last time you visited North Cyprus?")
    customer_experience_four = fields.Char(string="What was your purpose of visit?")
    customer_experience_five = fields.Char(string="What did you like most about North Cyprus?")
    customer_experience_comments = fields.Text(string="Comments")
    
    #goals and usage
    investment_experience = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Do you have any investment experience?")
    investment_country = fields.Many2one('res.country', string="Investment Country", help="Select the country where you have investment experience")
    investment_purpose = fields.Selection([
        ('profit', 'Profit'),
        ('tax', 'Tax'),
        ('self_use', 'Self-Use'),
        ('third_party_use', 'Third-Party Use'),
        ('immigration', 'Immigration'),
        ('exit_plan', 'Exit Plan'),
        ('asset_protection', 'Asset Protection/Extension'),
        ('company_construct', 'Company Construct'),
        ('inflation_protection', 'Inflation Protection'),
        ('other', 'Other')
    ], string="Investment Purpose", help="Select the primary purpose of the investment")
    investment_purpose_other = fields.Char(string="Other Investment Purpose", help="Please specify if 'Other' is selected")
    
    investment_type = fields.Selection([
        ('roi', 'Investment / Return on Investment (ROI)'),
        ('immigration', 'Immigration'),
        ('residential', 'Residential Property'),
        ('other', 'Other')
    ], string="Investment Type", help="Select the primary type of investment")
    investment_type_other = fields.Char(string="Other Investment Type", help="Please specify if 'Other' is selected")

    roi_subtype = fields.Selection([
        ('capital_gain', 'Capital Gain/Profit'),
        ('passive_income', 'Passive Income'),
        ('holiday_home', 'Holiday Home'),
        ('other', 'Other')
    ], string="ROI Subtype", help="Select the specific ROI investment type")
    roi_subtype_other = fields.Char(string="Other ROI Subtype", help="Please specify if 'Other' is selected")

    capital_gain_type = fields.Selection([
        ('buy_sell', 'Buy & Sell'),
        ('long_term', 'Long-term Investment'),
        ('portfolio', 'Build Portfolio'),
        ('short_term', 'Short-term Investment'),
        ('fix&flip', 'Fix & Flip'),   
        ('other', 'Other')
    ], string="Capital Gain Type", help="Select the type of capital gain investment")
    capital_gain_type_other = fields.Char(string="Other Capital Gain Type", help="Please specify if 'Other' is selected")

    buy_and_sell_period = fields.Selection([
        ('less_1_year', 'Less than 1 Year'),
        ('1_2_years', '1-2 Years'),
        ('2_3_years', '2-3 Years'),
        ('3_5_years', '3-5 Years'),
        ('more_5_years', 'More than 5 Years'),
        ('other', 'Other')
    ], string="Buy & Sell Period", help="Select the period for buy and sell investment")
    buy_and_sell_expected_profit=fields.Float(string="Expected Profit", help="Expected profit from buy and sell investment", digits=(16, 2))
    buy_and_sell_expected_period_other = fields.Char(string="Other Expected Profit", help="Please specify if 'Other' is selected")

    passive_income_type = fields.Selection([

        ('long_term_rental', 'Long-term Rental'),
        ('short_term_rental', 'Short-term Rental'),
        ('hotel_concept', 'Hotel Concept'),
        ('other', 'Other')
    ], string="Passive Income Type", help="Select the type of passive income investment")
    passive_income_type_other = fields.Char(string="Other Passive Income Type", help="Please specify if 'Other' is selected")

    holiday_home_type = fields.Selection([
        ('private', 'Private'),
        ('rent_available', 'Rent when Available'),
        ('other', 'Other')
    ], string="Holiday Home Type", help="Select the type of holiday home usage")
    holiday_home_type_other = fields.Char(string="Other Holiday Home Type", help="Please specify if 'Other' is selected")
    company_construct = fields.Text(string="Information about the company to be created")
    company_construct_sector = fields.Char(string="Sector of the company to be created")
    company_construct_number_of_employees = fields.Integer(string="Number of employees for the company to be created", help="Number of employees for the company to be created", default=0)
    company_construct_services_loaction = fields.Text(string="Services and location of the company to be created")

    

    immigration_question_one = fields.Char(string="Purpose of Immigration")
    immigration_question_two = fields.Char(string="How many people are you immigrating?")
    immigration_question_three = fields.Char(string="When do you plan to immigrate?")
    immigration_question_four = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Exit Plan?")

    #location and property type
    location = fields.Selection([
        ('seaside', 'Seaside'),
        ('montain-side', 'Montain-Side'),
        ('mountain_and_sea', 'Mountain and Sea side'),
        ('city-center', 'City-Center'),
        ('other', 'Other')
    ], string="Location", help="Select the location of the property")
    location_other = fields.Char(string="Other Location", help="Please specify if 'Other' is selected")

    distance_to_seaside = fields.Selection([
        ('less_500m', 'Less than 500m'),
        ('500m_1000m', '500m - 1000m'),
        ('1000m_2000m', '1000m - 2000m'),
        ('more_2000m', 'More than 2000m'),
        ('other', 'Other')
    ], string="Distance to Sea", help="Select the distance to the sea")
    distance_to_seaside_other = fields.Char(string="Other Distance to Sea", help="Please specify if 'Other' is selected")

    property_usage = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('rental', 'Rental'),
        ('other', 'Other')
    ], string="Property Usage", help="Select the usage of the property")
    property_usage_other = fields.Char(string="Other Property Usage", help="Please specify if 'Other' is selected")

    commercial_property_type = fields.Char(string="What type of commercial property are you looking for?")

    property_type = fields.Selection([
        ('resort', 'Resort'),
        ('detached', 'Detached'),
        ('high_rise', 'High Rise Building'),
        ('low_rise', 'Low Rise Building'),
        ('other', 'Other')
    ], string="Property Type", help="Select the type of property")
    property_type_other = fields.Char(string="Other Property Type", help="Please specify if 'Other' is selected")

    building_section = fields.Selection([
        ('ground_floor', 'Ground Floor'),
        ('lower_section', 'Lower Section'),
        ('middle_section', 'Middle Section'),
        ('top_section', 'Top Section'),
        ('penthouse_floor', 'Penthouse Floor'),
        ('other', 'Other')
    ], string="Building Section", help="Select the section of the building")
    building_section_other = fields.Char(string="Other Building Section", help="Please specify if 'Other' is selected")

    prefered_floor = fields.Integer(string="Prefered Floor", help="What is the floor of the property you are looking for?")
    
    property_type = fields.Selection([
        ('micro_apartment', 'Micro Apartment'),
        ('studio', 'Studio'),
        ('smart_studio_mansion', 'Smart Studio Mansion'),
        ('apartment', 'Apartment'),
        ('bungalow', 'Bungalow'),
        ('townhouse', 'Townhouse'),
        ('semi_detached', 'Semi Detached'),
        ('villa', 'Villa'),
        ('other', 'Other')
    ], string="Unit Type", help="Select the type of unit you are looking for")
    property_type_other = fields.Char(string="Other Unit Type", help="Please specify if 'Other' is selected")
    
    no_of_bedrooms = fields.Integer(string="Number of Bedrooms", help="How many bedrooms do you need?")
    no_of_bathrooms = fields.Integer(string="Number of Bathrooms", help="How many bathrooms do you need?")
    floor_type = fields.Selection([
        ('duplex', 'Duplex'),
        ('loft', 'Loft'),
        ('mezzanine', 'Mezzanine'),
        ('other', 'Other')
    ], string="Floor Type", help="Select the type of floor you are looking for")
    floor_type_other = fields.Char(string="Other Floor Type", help="Please specify if 'Other' is selected")



    # Interior and features
    property_feature_ids = fields.Many2many(
        'property.feature',
        'crm_lead_property_feature_rel',
        'lead_id',
        'feature_id',
        string='Property Features',
        domain="[('feature_type', '=', 'amenity')]",
        help="Select the amenities you are looking for"
    )

    interior_feature_ids = fields.Many2many(
        'property.feature',
        'crm_lead_interior_feature_rel',
        'lead_id',
        'feature_id',
        string='Interior Features',
        domain="[('feature_type', '=', 'interior')]",
        help="Select the interior features you are looking for"
    )

    infrastructure_feature_ids = fields.Many2many(
        'property.feature',
        'crm_lead_infrastructure_feature_rel',
        'lead_id',
        'feature_id',
        string='Infrastructure Features',
        domain="[('feature_type', '=', 'infrastructure')]",
        help="Select the infrastructure features you are looking for"
    )
    
    features = fields.Selection([
        ('communal_pool', 'Communal Pool'),
        ('gym_fitness', 'Gym/Fitness'),
        ('spa_wellness', 'SPA/Wellness'),
        ('outdoor_sports', 'Outdoor Sports'),
        ('restaurant', 'Restaurant'),
        ('cinema', 'Cinema'),
        ('hair_beauty_salon', 'Hair & Beauty Salon'),
        ('cctv_24_7', '24/7 CCTV'),
        ('kids_playground', 'Kids Playground'),
        ('car_park', 'Car Park'),
        ('other', 'Other')
    ], string="Features", help="Select the features you are looking for")
    features_other = fields.Char(string="Other Features", help="Please specify if 'Other' is selected")

    interior_features = fields.Selection([
        ('private_pool', 'Private Pool'),
        ('private_garden', 'Private Garden'), 
        ('heated_pool', 'Heated Pool'),
        ('smart_home', 'Smart Home'),
        ('basement', 'Basement'),
        ('balcony_terrace', 'Balcony/Terrace'),
        ('outdoor_kitchen', 'Outdoor Kitchen'),
        ('storage', 'Storage'),
        ('jacuzzi', 'Jacuzzi'),
        ('roof_terrace', 'Roof Terrace'),
        ('elevator', 'Elevator'),
        ('bbq_area', 'BBQ Area'),
        ('barrier_free', 'Barrier-free'),
        ('central_heating_cooling', 'Central Heating and Cooling'),
        ('solar_panel', 'Solar Panel'),
        ('pet_friendly', 'Pet-Friendly'),
        ('water_filter', 'Water Filter'),
        ('instant_hot_water', 'Instant Hot Water'),
        ('other', 'Other')
    ], string="Interior Features", help="Select the interior features you are looking for")
    interior_features_other = fields.Char(string="Other Interior Features", help="Please specify if 'Other' is selected")

    infrastructure = fields.Selection([
        ('university_school', 'University/School'),
        ('kindergarten_nursery', 'Kindergarten/Nursery'),
        ('hotel_casino', 'Hotel/Casino'),
        ('hospital_clinic', 'Hospital/Clinic'),
        ('pharmacy', 'Pharmacy'),
        ('supermarket', 'Supermarket'),
        ('restaurants_bars', 'Restaurants/Bars'),
        ('shopping_center_mall', 'Shopping Center/Mall'),
        ('banks_atm', 'Banks/ATM'),
        ('clubs_nightlife', 'Clubs/Night-life'),
        ('mosque_church', 'Mosque/Church'),
        ('marina', 'Marina'),
        ('fiat_crypto_exchange', 'Fiat & Crypto Exchange'),
        ('hair_beauty_salon', 'Hair & Beauty Salon'),
        ('airport', 'Airport'),
        ('other', 'Other')
    ], string="Infrastructure", help="Select the infrastructure you are looking for in the area")
    infrastructure_other = fields.Char(string="Other Infrastructure", help="Please specify if 'Other' is selected")

    interior_design = fields.Selection([
        ('custom', 'Custom'),
        ('package', 'Package'),
        ('other', 'Other')
    ], string="Interior Design Type")
    interior_design_other = fields.Char(string="Other Interior Design Type", help="Please specify if 'Other' is selected")

    furniture_package = fields.Selection([
        ('low_budget', 'Low Budget'),
        ('standard', 'Standard'), 
        ('luxury', 'Luxury'),
        ('other', 'Other')
    ], string="Furniture Package")
    furniture_package_other = fields.Char(string="Other Furniture Package", help="Please specify if 'Other' is selected")

    appliances_package = fields.Selection([
        ('low_budget', 'Low Budget'),
        ('standard', 'Standard'),
        ('luxury', 'Luxury'),
        ('other', 'Other')
    ], string="White Goods/AC Package")
    appliances_package_other = fields.Char(string="Other White Goods/AC Package", help="Please specify if 'Other' is selected")

    interior_design_notes = fields.Text(string="Interior Design Comments")

    property_situation = fields.Selection([
        ('resale', 'Resale'),
        ('off_plan', 'Off Plan'),
        ('under_construction', 'Under Construction'),
        ('new_build', 'New Build'),
        ('other', 'Other')
    ], string="Property Situation")
    property_situation_other = fields.Char(string="Other Property Situation", help="Please specify if 'Other' is selected")

    move_before_completion = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Move in Before Completion?")

    situation_notes = fields.Text(string="Property Situation Comments")

    quality_preference = fields.Selection([
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('high', 'High'),
        ('other', 'Other')
    ], string="Quality Preference")
    quality_preference_other = fields.Char(string="Other Quality Preference", help="Please specify if 'Other' is selected")

    budget_level = fields.Selection([
        ('low', 'Low'),
        ('standard', 'Standard'),
        ('high', 'High'),
        ('other', 'Other')
    ], string="Budget Level")
    budget_level_other = fields.Char(string="Other Budget Level", help="Please specify if 'Other' is selected")

    # Financial Resources
    payment_type = fields.Selection([
        ('full', 'Full Payment'),
        ('stage', 'Stage Payment'),
        ('plan', 'Payment Plan'),
       
    ], string="Payment Type")
    payment_type_other = fields.Char(string="Other Payment Type", help="Please specify if 'Other' is selected")


    initial_payment_amount = fields.Float(string='Initial Payment Amount', digits=(16, 2))


    monthly_amount = fields.Float(string='Monthly Installment Amount', digits=(16, 2))

 
    budget_amount = fields.Float(string='Total Budget Amount', digits=(16, 2))


    deposit_amount = fields.Float(string='Reservation Deposit Amount', digits=(16, 2))

    payment_plan_years = fields.Selection([
        ('1', '1 Year'),
        ('2', '2 Years'), 
        ('3', '3 Years'),
        ('4', '4 Years'),
        ('5', '5 Years'),
        ('6', '6 Years'),
        ('7', '7 Years'),
        ('8', '8 Years'),
        ('9', '9 Years'),
        ('10', '10 Years')
        
    ], string="Payment Plan Duration")
    payment_plan_years_other = fields.Char(string="Other Payment Plan Duration", help="Please specify if 'Other' is selected")

    # Assets for Sale
    car_for_sale = fields.Char(string="Car for Sale Details")
    house_for_sale = fields.Char(string="House for Sale Details") 
    office_for_sale = fields.Char(string="Office for Sale Details")
    other_assets_for_sale = fields.Char(string="Other Assets for Sale Details")

 
    assets_for_sale = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     string='Assets for Sale',
     domain="[('feature_type', '=', 'assets')]",
     help="Select the assets for sale you are looking for"
   )
    car_assets_visible = fields.Boolean(
        string="Assets Visible", 
        compute="_compute_assets_for_sale", 
        store=True)
    house_assets_visible = fields.Boolean(
        string="Assets Visible", 
        compute="_compute_assets_for_sale", 
        store=True)
    office_assets_visible = fields.Boolean(
        string="Assets Visible",
        compute="_compute_assets_for_sale",
        store=True)
    other_assets_visible = fields.Boolean(
        string="Assets Visible",
        compute="_compute_assets_for_sale",
        store=True)
    # Financial Details
    savings = fields.Float(string="Savings", digits=(16,2))
    crypto_savings = fields.Float(string="Crypto Savings", digits=(16,2))
    available_liquidity = fields.Float(string="Available Liquidity", digits=(16,2))
    future_liquidity = fields.Float(string="Future Liquidity", digits=(16,2))
    down_payment = fields.Float(string="Down Payment", digits=(16,2))
    total_budget = fields.Float(string="Total Budget", digits=(16,2))
    reservation_deposit = fields.Float(string="Reservation Deposit", digits=(16,2))
    installment_rates = fields.Float(string="Installment Rates", digits=(16,2))
    financial_resources_comments = fields.Char(string="Financial Resources Comments")

    # Necessities & After Sales Services
    permit_needs = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     string='Permit Needs',
     domain="[('feature_type', '=', 'permit_needs')]",
     help="Select the assets for sale you are looking for"
   )

    education_needs = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     string='Education Needs',
     domain="[('feature_type', '=', 'education_needs')]",
     help="Select the assets for sale you are looking for"
   )

    insurance_needs = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     string='Insurance Needs',
     domain="[('feature_type', '=', 'insurance_needs')]",
     help="Select the assets for sale you are looking for"
   )

    legal_needs = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     string='Legal Needs',
     domain="[('feature_type', '=', 'legal_needs')]",
     help="Select the assets for sale you are looking for"
   )

    car_needs = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     string='Car Needs',
     domain="[('feature_type', '=', 'car_needs')]",
     help="Select the assets for sale you are looking for"
   )

    investment_needs = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     string='Investment Needs',
     domain="[('feature_type', '=', 'investment_needs')]",
     help="Select the assets for sale you are looking for"
   )

    banking_needs = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     domain="[('feature_type', '=', 'banking_needs')]",
     help="Select the assets for sale you are looking for"
   )

    # Cooperation Possibilities
    cooperation_type = fields.Many2many(
     'property.feature',
     'crm_lead_assets_feature_rel', 
     'lead_id',
     'feature_id',
     domain="[('feature_type', '=', 'cooperation')]",
     help="Select the assets for sale you are looking for"
   )
   
    #customer preferences
    
    # # Attached agents should be specific partners that are agents
    # attached_agent = fields.Many2many(
    #     'res.partner', 
    #     string="Attached Agent", 
    #     domain=[('is_agent', '=', True)]
    # )
    
    

    

    # Placeholder for PDF import button
    def action_import_analysis_from_pdf(self):
        # To be implemented in future
        pass
    
    @api.depends('partner_id')
    def _compute_partner_info(self):
            for record in self:
                if record.partner_id:
                    # Automatically update partner_contact_info from partner_id
                    record.partner_contact_info = record.partner_id.contact_info

    def create(self, vals):
        lead = super().create(vals)
        if vals.get('user_ids'):
            lead._assign_salespersons(vals.get('user_ids'))

        return lead

    def write(self, vals):
        for record in self:
            # Check if the user_ids are being modified
            if 'user_ids' in vals:
                # If user_ids are being changed, ensure the user is either an admin
                # or the owner of the lead (the user who created it)
                if not self.env.user.has_group('base.group_system') and record.create_uid != self.env.user:
                    raise UserError("You can only change the salespersons if you are the owner of the lead.")

        # Call the super method to apply the write action after the checks
        return super(CrmLead, self).write(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmLead, self).fields_view_get(view_id, view_type, toolbar, submenu)

        if view_type == 'form':
            # Get the XML definition of the form view
            doc = etree.XML(res['arch'])

            # Loop through all the <field> elements in the view for 'user_ids'
            for field in doc.xpath("//field[@name='user_ids']"):
                # If the current user is not the original user_id, make the field readonly
                if self.user_id != self.env.user:
                    field.set('readonly', '1')

            # Modify the res['arch'] with the updated XML
            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

    @api.depends('vip_status')
    def _compute_is_bank_services_readonly(self):
        for record in self:
            record.is_bank_services_readonly = record.vip_status == 'vip'
    @api.depends('car_for_sale', 'house_for_sale', 'office_for_sale', 'other_assets_for_sale')
    def _compute_assets_for_sale(self):
        for record in self:
            record.assets_for_sale = any([
                record.car_for_sale,
                record.house_for_sale,
                record.office_for_sale,
                record.other_assets_for_sale
            ])

    @api.onchange('assets_for_sale')
    def _onchange_assets_for_sale(self):
        if self.assets_for_sale:
            self.car_assets_visible = any(lang.name == 'Car' for lang in self.assets_for_sale)
            self.house_assets_visible = any(lang.name == 'House' for lang in self.assets_for_sale)
            self.office_assets_visible = any(lang.name == 'Office' for lang in self.assets_for_sale)
            self.other_assets_visible = any(lang.name == 'Other' for lang in self.assets_for_sale)
        else:
            self.car_assets_visible = False
            self.house_assets_visible = False
            self.office_assets_visible = False
            self.other_assets_visible = False

