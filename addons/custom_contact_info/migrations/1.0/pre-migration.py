def migrate(cr, version):
    # Add primary_language_id column to res_partner
    cr.execute("""
        ALTER TABLE res_partner 
        ADD COLUMN IF NOT EXISTS primary_language_id integer 
        REFERENCES custom_language(id) ON DELETE SET NULL;
    """)
