from odoo import models, fields, api

class AgentCommissionLine(models.Model):
    _name = 'crm.agent.commission.line'
    _description = 'Agent Commission Line'

    lead_id = fields.Many2one('crm.lead', string="Lead", ondelete="cascade", required=True)
    agent_id = fields.Many2one('res.users', string='Agent', required=True)
    commission = fields.Float(string='Commission', digits=(5, 2))

# class CrmLeadChild(models.Model):
#     _name = 'crm.lead.child'
#     _description = 'CRM Lead Child Information'

#     lead_id = fields.Many2one('crm.lead', string='Lead', required=True, ondelete='cascade')
#     age = fields.Integer(string='Age', required=True)
#     gender = fields.Selection([
#         ('male', 'Male'),
#         ('female', 'Female'),
#         ('other', 'Other')
#     ], string='Gender', required=True)

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    #customer information
    referral_source = fields.Many2one('res.partner', string="Referral Source", help="Select the person or company who referred this lead")
    referees_commission = fields.Float(string="Commission", digits=(5, 2))
    sales_commission_percent = fields.Float(string="Commission", digits=(5, 2))
    agent_commission_lines = fields.One2many('crm.agent.commission.line', 'lead_id', string='Additional Agents')
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

    
    lead_quality = fields.Selection(
        selection=[
            ('0', 'Very Low'),
            ('1', 'Low'),
            ('2', 'Medium'),
            ('3', 'High'),
            ('4', 'Very High')
        ],
        string='Lead Quality',
        index=True,
        default='0',  
        help="Use this to prioritize your leads: the higher the priority, the more important the lead."
    )
    #personal information
    employment_status = fields.Selection([
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('retired', 'Retired'),
        ('unemployed', 'Unemployed'),
        ('other', 'Other')
    ], string="Employment Status")
    employment_status_other = fields.Char(string="Other Employment Status", help="Please specify if 'Other' is selected")
    occupation = fields.Char(string="Occupation")
    
    # Income fields with currency
    income = fields.Float(
        string="Income",
        digits=(16, 2))
    
    additional_income = fields.Float(
        string="Additional Income", 
        digits=(16, 2),
    )
    
    languages = fields.Many2many(
        'custom.language',
        string='Languages',
        relation='crm_lead_lang_rel',
        column1='lead_id',
        column2='lang_id'
    )
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('partner', 'Partner'),
        ('divorced', 'Divorced')
    ], string="Marital Status")
    

    #partner information
    partner_first_name = fields.Char(string="Partner First Name")
    partner_last_name = fields.Char(string="Partner Last Name")
    partner_nationality = fields.Many2one('res.country', string="Partner Nationality")
    partner_city = fields.Char(string="Partner City")
    partner_country = fields.Many2one('res.country', string="Partner Country")
    partner_employment_status = fields.Selection([
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('retired', 'Retired'),
        ('unemployed', 'Unemployed'),
        ('other', 'Other')
    ], string="Partner Employment Status")
    partner_employment_status_other = fields.Char(string="Other Partner Employment Status", help="Please specify if 'Other' is selected")
    partner_occupation = fields.Char(string="Partner Occupation")
    
    # Partner Income fields with currency
    partner_income = fields.Float(string="Partner Income", digits=(16, 2))
    
    
    partner_additional_income = fields.Float(string="Partner Additional Income", digits=(16, 2))
    
    partner_languages = fields.Many2many(
        'custom.language',
        string='Partner Languages',
        relation='crm_lead_partner_lang_rel',
        column1='lead_id',
        column2='lang_id'
    )
    
    #children information
    age = fields.Integer(string="Child 1 Age")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
        
    ], string="Child 1 Gender")

    age2 = fields.Integer(string="Child 2 Age") 
    gender2 = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Child 2 Gender")

    age3 = fields.Integer(string="Child 3 Age")
    gender3 = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Child 3 Gender")

    age4 = fields.Integer(string="Child 4 Age")
    gender4 = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
        
    ], string="Child 4 Gender")

    age5 = fields.Integer(string="Child 5 Age")
    gender5 = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
        
    ], string="Child 5 Gender")
    personal_question1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Are you currently living with your children ? ")

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
        ('other', 'Other')
    ], string="Capital Gain Type", help="Select the type of capital gain investment")
    capital_gain_type_other = fields.Char(string="Other Capital Gain Type", help="Please specify if 'Other' is selected")

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

    # Multiple Currency and Amount fields
    currency_id = fields.Selection([
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('USD', 'US Dollar ($)')
    ], string='Default Currency', default='EUR')
    
    # Initial Payment
    initial_payment_currency = fields.Selection([
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('USD', 'US Dollar ($)')
    ], string='Initial Payment Currency', default='EUR')
    initial_payment_amount = fields.Float(string='Initial Payment Amount', digits=(16, 2))

    # Monthly Installment
    monthly_currency = fields.Selection([
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('USD', 'US Dollar ($)')
    ], string='Monthly Installment Currency', default='EUR')
    monthly_amount = fields.Float(string='Monthly Installment Amount', digits=(16, 2))

    # Total Budget
    budget_currency = fields.Selection([
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('USD', 'US Dollar ($)')
    ], string='Budget Currency', default='EUR')
    budget_amount = fields.Float(string='Total Budget Amount', digits=(16, 2))

    # Reservation Deposit
    deposit_currency = fields.Selection([
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('USD', 'US Dollar ($)')
    ], string='Deposit Currency', default='EUR')
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

    @api.onchange('children_count')
    def _onchange_children_count(self):
        # Adjust child_ids based on children_count
        if self.children_count < 0:
            self.children_count = 0
        current_count = len(self.child_ids)
        if self.children_count > current_count:
            # Add new child records
            new_records = [(0, 0, {'age': 0, 'gender': 'male'}) for _ in range(self.children_count - current_count)]
            self.child_ids = [(4, child.id) for child in self.child_ids] + new_records
        elif self.children_count < current_count:
            # Remove excess child records
            self.child_ids = [(6, 0, self.child_ids[:self.children_count].ids)]

    @api.constrains('children_count')
    def _check_children_count(self):
        for lead in self:
            if lead.children_count != len(lead.child_ids):
                lead.children_count = len(lead.child_ids)
